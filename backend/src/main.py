import uvicorn
from fastapi import FastAPI, HTTPException, Query, status, Response, Depends, Request, BackgroundTasks, Form, File, UploadFile
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2, OAuth2PasswordRequestForm, OAuth2PasswordBearer, APIKeyHeader
from fastapi.security.utils import get_authorization_scheme_param
from contextlib import asynccontextmanager
from sqlalchemy.orm import selectinload
from gallery import get_client, models, utils, config, auth
import datetime
from sqlmodel import Session, SQLModel, select
import typing
import httpx
import jwt
from jwt.exceptions import InvalidTokenError, MissingRequiredClaimError, DecodeError
from sqlalchemy import and_
from pydantic import BaseModel
import datetime
from functools import wraps
from urllib.parse import urlencode
import pathlib
import shutil
from google.oauth2 import id_token
from google.auth.transport import requests


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('startingup')
    yield
    print('closingdown')

app = FastAPI(lifespan=lifespan)
c = get_client()

assert c.header_keys['auth_error'] == auth.AUTH_ERROR_HEADER


def jwt_encode(payload: dict):
    return jwt.encode(payload, c.jwt_secret_key, algorithm=c.jwt_algorithm)


def jwt_decode(token: str):
    return jwt.decode(token, c.jwt_secret_key, algorithms=[c.jwt_algorithm])


class OAuth2PasswordBearerMultiSource(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: typing.Optional[str] = None,
        scopes: typing.Optional[dict[str, str]] = None,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(
            password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=False)

    async def __call__(self, request: Request) -> str | None:
        # change to accept access token from Authorization header

        authorization = request.headers.get("Authorization")
        if authorization:
            scheme, param = get_authorization_scheme_param(authorization)
            if scheme.lower() == "bearer":
                return param

        # HTTP-only Cookie
        cookie_access_token = request.cookies.get(
            c.cookie_keys['access_token'])
        if cookie_access_token:
            return cookie_access_token

        return None


oauth2_scheme = OAuth2PasswordBearerMultiSource(
    tokenUrl="token/")


class DetailOnlyResponse(BaseModel):
    detail: str


class NotFoundResponse(DetailOnlyResponse):
    pass


class ItemAvailableResponse(BaseModel):
    available: bool


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):

    response = JSONResponse(status_code=exc.status_code,
                            content={"detail": exc.detail}, headers=exc.headers)

    if exc.headers and exc.headers.get(auth.AUTH_ERROR_HEADER) != None:
        delete_access_token_cookie(response)
    return response


def set_access_token_cookie(access_token: str, response: Response, stay_signed_in: bool):

    kwargs = {}
    if stay_signed_in:
        kwargs['expires'] = datetime.datetime.now(
            datetime.UTC) + c.authentication['default_expiry_timedelta']

    response.set_cookie(
        key=c.cookie_keys['access_token'],
        value=access_token,
        httponly=True,
        secure=True,
        samesite="Lax",
        **kwargs
    )


def delete_access_token_cookie(response: Response):
    response.delete_cookie(c.cookie_keys['access_token'])


class GetAuthorizationReturn(BaseModel):
    isAuthorized: bool = False
    expiry: typing.Optional[datetime.datetime] = None
    exception: typing.Optional[auth.EXCEPTION] = None
    user: typing.Optional[models.UserPrivate] = None
    scope_ids: typing.Optional[set[models.ScopeTypes.id]] = None
    auth_credential: typing.Optional[models.AUTH_CREDENTIAL_MODEL] = None


def get_authorization(
    required_scopes: set[models.ScopeTypes.name] = set(),
    raise_exceptions: bool = True,
    permitted_auth_credential_types: set[models.AuthCredentialTypes.type] = set(
        key for key in models.AUTH_CREDENTIAL_MODEL_MAPPING),
    override_lifetime: datetime.timedelta | None = None,
) -> typing.Callable[[str], GetAuthorizationReturn]:

    async def dependecy(response: Response, auth_token: typing.Annotated[str | None, Depends(oauth2_scheme)]) -> GetAuthorizationReturn:
        async def inner() -> GetAuthorizationReturn:
            # attempt to decode the jwt

            if auth_token == None:
                return GetAuthorizationReturn(exception='improper_format')

            try:
                payload: models.AuthCredential.JWTExport = jwt_decode(
                    auth_token)
            except:
                return GetAuthorizationReturn(exception='improper_format')

            # validate the jwt claims
            if not models.AuthCredential.validate_jwt_claims(payload):
                return GetAuthorizationReturn(exception='missing_required_claims')

            # make sure the type is permitted
            if payload['type'] not in permitted_auth_credential_types:
                return GetAuthorizationReturn(exception='invalid_authorization_type')

            auth_credential_dict = models.AuthCredential.import_from_jwt(
                payload)
            auth_credential: models.AUTH_CREDENTIAL_MODEL | None = None

            with Session(c.db_engine) as session:

                auth_credential = await models.AUTH_CREDENTIAL_MODEL_MAPPING[auth_credential_dict['type']].get_one_by_id(
                    session, auth_credential_dict['id']
                )

                # not in the db, raise exception
                if not auth_credential:
                    return GetAuthorizationReturn(exception='authorization_expired')

                dt_now = datetime.datetime.now(datetime.UTC)
                dt_exp_jwt = datetime.datetime.fromtimestamp(
                    payload['exp'], datetime.UTC)
                dt_exp_db = auth_credential.expiry.replace(tzinfo=datetime.UTC)
                dt_exp = min(dt_exp_jwt, dt_exp_db)

                if dt_now > dt_exp:
                    await auth_credential.delete_one_by_id(
                        session, auth_credential.id)
                    return GetAuthorizationReturn(exception='authorization_expired')

                # if there was an overriden lifetime, check if it has expired
                if override_lifetime != None:
                    # take the minimum of the hardcoded jwt and database value, ### note: redundancy needed or not?

                    dt_ait_jwt = datetime.datetime.fromtimestamp(
                        payload['iat'], datetime.UTC)
                    dt_ait_db = auth_credential.issued.replace(
                        tzinfo=datetime.UTC)

                    if dt_now > (min(dt_ait_jwt, dt_ait_db) + override_lifetime):
                        await auth_credential.delete_one_by_id(
                            session, auth_credential.id)
                        return GetAuthorizationReturn(exception='authorization_expired')

                user = auth_credential.user
                if user == None:
                    return GetAuthorizationReturn(exception='user_not_found')

                # get the scopes for the user
                scope_ids: set[models.ScopeTypes.id] = set()

                if auth_credential.type == 'access_token':
                    scope_ids = c.user_role_id_scope_ids[user.user_role_id]
                elif auth_credential.type == 'api_key':
                    auth_credential: models.ApiKey
                    scope_ids = await auth_credential.get_scope_ids()

                required_scope_ids = set(
                    [c.scope_name_mapping[scope_name]
                        for scope_name in required_scopes]
                )

                if not required_scope_ids.issubset(scope_ids):
                    return GetAuthorizationReturn(exception='not_permitted')

                return GetAuthorizationReturn(
                    isAuthorized=True,
                    expiry=dt_exp,
                    user=models.UserPrivate.model_validate(user),
                    scope_ids=scope_ids,
                    auth_credential=auth_credential,
                )

        inner_response = await inner()
        if inner_response.exception:

            exception_to_raise = auth.EXCEPTION_MAPPING[inner_response.exception](
            )

            if exception_to_raise.status_code in {status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED, status.HTTP_404_NOT_FOUND}:
                delete_access_token_cookie(response)

            if raise_exceptions:
                raise exception_to_raise

        return inner_response

    return dependecy


class GetAuthBaseReturn(BaseModel):
    user: typing.Optional[models.UserPrivate]
    scope_ids: typing.Optional[set[models.ScopeTypes.id]]
    expiry: typing.Optional[models.AuthCredentialTypes.expiry]


assert c.auth_key == 'auth'


class GetAuthReturn(BaseModel):
    auth: GetAuthBaseReturn


def get_auth(get_authorization_return: GetAuthorizationReturn) -> GetAuthReturn:
    return GetAuthReturn(auth=GetAuthBaseReturn(
        user=get_authorization_return.user,
        scope_ids=get_authorization_return.scope_ids,
        expiry=get_authorization_return.expiry
    ))


@ app.get('/auth/')
async def auth_root(authorization: typing.Annotated[GetAuthorizationReturn, Depends(get_authorization(raise_exceptions=False))]) -> GetAuthReturn:
    return get_auth(authorization)


async def authenticate_user_with_username_and_password(form_data: typing.Annotated[OAuth2PasswordRequestForm, Depends()]) -> models.User:
    with Session(c.db_engine) as session:
        user = await models.User.authenticate(
            session, form_data.username, form_data.password)
        if not user:
            raise auth.credentials_exception()
        return user


@ app.post('/token/')
async def post_token(
    user: typing.Annotated[models.User, Depends(authenticate_user_with_username_and_password)],
    response: Response,
    stay_signed_in: bool = Form(c.authentication['stay_signed_in_default'])
):

    with Session(c.db_engine) as session:
        auth_credential = await models.UserAccessTokenCreateAdmin(
            user_id=user.id, lifespan=c.authentication['default_expiry_timedelta']).create()
        auth_credential.add_to_db(session)
        set_access_token_cookie(jwt_encode(
            auth_credential.export_to_jwt()), response, stay_signed_in)

    return


class LoginResponse(GetAuthReturn):
    pass


@ app.post('/auth/login/password/', responses={status.HTTP_401_UNAUTHORIZED: {'description': 'Could not validate credentials', 'model': DetailOnlyResponse}})
async def login(
    user: typing.Annotated[models.User, Depends(authenticate_user_with_username_and_password)],
    response: Response,
    stay_signed_in: bool = Form(c.authentication['stay_signed_in_default'])
) -> LoginResponse:

    with Session(c.db_engine) as session:

        user_access_token = await models.UserAccessTokenCreateAdmin(
            user_id=user.id, lifespan=c.authentication['default_expiry_timedelta']).create()
        await user_access_token.add_to_db(session)
        set_access_token_cookie(jwt_encode(
            user_access_token.export_to_jwt()), response, stay_signed_in)

        return LoginResponse(
            auth=GetAuthBaseReturn(
                user=models.UserPrivate.model_validate(user),
                scope_ids=set(
                    c.user_role_id_scope_ids[user.user_role_id]),
                expiry=user_access_token.expiry
            )
        )


class SignupResponse(GetAuthReturn):
    pass


@ app.post('/auth/signup/', responses={status.HTTP_409_CONFLICT: {"description": 'User already exists', 'model': DetailOnlyResponse}})
async def sign_up(
    response: Response,
    email: models.UserTypes.email = Form(...),
    password: models.UserTypes.password = Form(...),
    stay_signed_in: bool = Form(c.authentication['stay_signed_in_default'])
) -> SignupResponse:

    user_create_admin = models.UserCreateAdmin(
        email=email, password=password, user_role_id=c.user_role_name_mapping['user'])

    with Session(c.db_engine) as session:
        user = await user_create_admin.post(session)

        user_access_token = await models.UserAccessTokenCreateAdmin(
            user_id=user.id, type='access_token', lifespan=c.authentication['default_expiry_timedelta']).create()
        await user_access_token.add_to_db(session)
        set_access_token_cookie(jwt_encode(
            user_access_token.export_to_jwt()), response, stay_signed_in)

        return SignupResponse(auth=auth)


class LoginWithEmailMagicLinkRequest(BaseModel):
    email: models.UserTypes.email
    stay_signed_in: bool = False


async def send_magic_link_to_email(model: LoginWithEmailMagicLinkRequest):

    with Session(c.db_engine) as session:
        user = await models.User.get_one_by_key_values(
            session, {'email': model.email})

        if user:
            user_access_token = await models.UserAccessTokenCreateAdmin(
                user_id=user.id, lifespan=c.authentication['magic_link_expiry_timedelta']).create()
            await user_access_token.add_to_db(session)

            link_data = {
                'access_token': jwt_encode(user_access_token.export_to_jwt()),
                'stay_signed_in': model.stay_signed_in
            }

            print('beep boop beep... sending email')
            print('http://localhost:3000' +
                  c.magic_link_frontend_url +
                  '?' + urlencode(link_data)
                  )

    # still need to fill this function in!


@ app.post('/auth/login/email-magic-link/')
async def login_with_email_magic_link(model: LoginWithEmailMagicLinkRequest, background_tasks: BackgroundTasks) -> DetailOnlyResponse:
    background_tasks.add_task(send_magic_link_to_email, model)
    return DetailOnlyResponse(detail='If an account with this email exists, a login link has been sent.')


class VerifyMagicLinkRequest(BaseModel):
    stay_signed_in: bool = False


class VerifyMagicLinkResponse(GetAuthReturn):
    pass


@ app.post('/auth/verify-magic-link/', responses={status.HTTP_401_UNAUTHORIZED: {'description': 'Invalid token', 'model': DetailOnlyResponse}})
async def verify_magic_link(model: VerifyMagicLinkRequest, authorization: typing.Annotated[GetAuthorizationReturn, Depends(get_authorization(permitted_auth_credential_types={'access_token'},
                                                                                                                                             override_lifetime=c.authentication['magic_link_expiry_timedelta']))], response: Response) -> VerifyMagicLinkResponse:
    with Session(c.db_engine) as session:

        user_access_token = await models.UserAccessTokenCreateAdmin(
            user_id=authorization.user.id, lifespan=c.authentication['default_expiry_timedelta']).create()
        await user_access_token.add_to_db(session)
        set_access_token_cookie(jwt_encode(
            user_access_token.export_to_jwt()), response, model.stay_signed_in
        )

        # one time link, delete the auth_credential
        await models.UserAccessToken.delete_one_by_id(
            session, authorization.auth_credential.id)

        return VerifyMagicLinkResponse(
            auth=GetAuthBaseReturn(
                user=models.UserPrivate.model_validate(authorization.user),
                scope_ids=set(
                    c.user_role_id_scope_ids[authorization.user.user_role_id]),
                expiry=user_access_token.expiry
            )
        )


class GoogleAuthResponse(LoginResponse):
    pass


class GoogleAuthRequest(BaseModel):
    access_token: str


@ app.post("/auth/login/google/", responses={status.HTTP_400_BAD_REQUEST: {"description": 'Invalid token'}})
async def login_with_google(request_token: GoogleAuthRequest, response: Response) -> GoogleAuthResponse:
    async with httpx.AsyncClient() as client:
        res = await client.get('https://www.googleapis.com/oauth2/v3/userinfo?access_token={}'.format(request_token.access_token))
        res.raise_for_status()
        user_info = res.json()

    # fields: sub, name, given_name, family_name, picture, email, email_verified
    email = user_info.get('email')
    if not email:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            detail='Invalid token')
    with Session(c.db_engine) as session:
        user = await models.User.get_one_by_key_values(session, {'email': email})
        if not user:
            user_create_admin = models.UserCreateAdmin(
                email=email,
            )
            user = await user_create_admin.post(session)

        user_access_token = await models.UserAccessTokenCreateAdmin(
            user_id=user.id, lifespan=c.authentication['default_expiry_timedelta']).create()
        await user_access_token.add_to_db(session)
        set_access_token_cookie(jwt_encode(
            user_access_token.export_to_jwt()), response)

        return VerifyMagicLinkResponse(
            auth=GetAuthBaseReturn(
                user=models.UserPrivate.model_validate(user),
                scope_ids=set(
                    c.user_role_id_scope_ids[user.user_role_id]),
                expiry=user_access_token.expiry
            )
        )


@ app.post('/auth/logout/')
async def logout(response: Response, authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(raise_exceptions=False, permitted_auth_credential_types={'access_token'}))]) -> DetailOnlyResponse:

    if authorization.auth_credential:
        if authorization.auth_credential.type == 'access_token':
            with Session(c.db_engine) as session:
                await models.UserAccessToken.delete_one_by_id(session,
                                                              authorization.auth_credential.id)

    delete_access_token_cookie(response)
    return DetailOnlyResponse(detail='Logged out')

# # USERS


@app.get('/admin/users/{user_id}', responses={status.HTTP_404_NOT_FOUND: {"description": models.User.not_found_message(), 'model': NotFoundResponse}})
async def get_user_by_id_admin(
    user_id: models.UserTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))]
) -> models.User:
    with Session(c.db_engine) as session:
        return await models.User.get(session, user_id)


@app.post('/admin/users/', responses={status.HTTP_409_CONFLICT: {"description": 'User already exists', 'model': DetailOnlyResponse}})
async def post_user_admin(
    user_create: models.UserCreateAdmin,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))]
) -> models.User:
    with Session(c.db_engine) as session:
        return await user_create.post(session)


@app.patch('/admin/users/{user_id}/', responses={status.HTTP_400_BAD_REQUEST: {"description": 'User id in url does not match user id in body'}})
async def patch_user_admin(
    user_id: models.UserTypes.id,
    user_update_admin: models.UserUpdateAdmin,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))]
) -> models.User:

    if user_id != user_update_admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='User id in url does not match user id in body')

    with Session(c.db_engine) as session:
        return user_update_admin.patch(session)


@app.delete('/admin/users/{user_id}/', status_code=status.HTTP_204_NO_CONTENT, responses={})
async def delete_user_admin(
    user_id: models.UserTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))]
):
    with Session(c.db_engine) as session:
        if await models.User.delete(session, user_id):
            return Response(status_code=status.HTTP_204_NO_CONTENT)


@ app.get('/users/available/username/{username}/')
async def user_username_available(username: models.UserTypes.username) -> ItemAvailableResponse:
    with Session(c.db_engine) as session:
        return ItemAvailableResponse(available=await models.User.is_username_available(session, username))


@ app.get('/users/available/email/{email}/')
async def user_email_available(email: models.UserTypes.email) -> ItemAvailableResponse:
    with Session(c.db_engine) as session:
        return ItemAvailableResponse(available=await models.User.is_email_available(session, email))


@app.get('/user/', responses={status.HTTP_404_NOT_FOUND: {"description": models.User.not_found_message(), 'model': NotFoundResponse}})
async def get_user(authorization: typing.Annotated[GetAuthorizationReturn, Depends(get_authorization())]) -> models.UserPrivate:
    return models.UserPrivate.model_validate(authorization.user)


@ app.patch('/user/', responses={
    status.HTTP_404_NOT_FOUND: {"description": models.User.not_found_message(), 'model': NotFoundResponse},
    status.HTTP_409_CONFLICT: {"description": 'Username or email already exists', 'model': DetailOnlyResponse},
})
async def patch_user(
    user_update: models.UserUpdate,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization())]
) -> models.UserPrivate:
    with Session(c.db_engine) as session:
        user = models.UserUpdateAdmin(
            **user_update.model_dump(), id=authorization.user.id
        ).patch(session)
        return models.UserPrivate.model_validate(user)


@ app.delete('/user/', status_code=status.HTTP_204_NO_CONTENT, responses={
    status.HTTP_404_NOT_FOUND: {
        "description": models.User.not_found_message(), 'model': NotFoundResponse}
}
)
async def delete_user(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization())]
) -> Response:
    with Session(c.db_engine) as session:
        if models.User.delete(session, authorization.user.id):
            return Response(status_code=status.HTTP_204_NO_CONTENT)

#
# User Access Tokens
#


@app.get('/admin/user-access-tokens/{user_access_token_id}', responses={status.HTTP_404_NOT_FOUND: {"description": models.UserAccessToken.not_found_message(), 'model': NotFoundResponse}})
async def get_user_access_token_by_id_admin(
    user_access_token_id: models.UserAccessTokenTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))]
) -> models.UserAccessToken:
    with Session(c.db_engine) as session:
        return await models.UserAccessToken.get(session, user_access_token_id)


@app.post('/admin/user-access-tokens/', responses={status.HTTP_409_CONFLICT: {"description": 'User already exists', 'model': DetailOnlyResponse}})
async def post_user_access_token_admin(
    user_access_token_create_admin: models.UserAccessTokenCreateAdmin,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))]
) -> models.UserAccessToken:
    with Session(c.db_engine) as session:
        return user_access_token_create_admin.post(session)


@app.patch('/admin/user-access-tokens/{user_access_token_id}/', responses={status.HTTP_400_BAD_REQUEST: {"description": 'User access token id in url does not match user access token id in body'}})
async def patch_user_access_token_admin(
    user_access_token_id: models.UserAccessTokenTypes.id,
    user_access_token_update_admin: models.UserAccessTokenUpdateAdmin,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))]
) -> models.User:

    if user_access_token_id != user_access_token_update_admin._id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='User access token id in url does not match user access token id in body')

    with Session(c.db_engine) as session:
        return user_access_token_update_admin.patch(session)


@app.delete('/admin/user-access-tokens/{user_access_token_id}/', status_code=status.HTTP_204_NO_CONTENT, responses={status.HTTP_404_NOT_FOUND: {"description": models.UserAccessToken.not_found_message(), 'model': NotFoundResponse}})
async def delete_user_admin(
    user_access_token_id: models.UserAccessTokenTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))]
):
    with Session(c.db_engine) as session:
        if models.UserAccessToken.delete(session, user_access_token_id):
            return Response(status_code=status.HTTP_204_NO_CONTENT)


@ app.get('/user-access-tokens/', responses={status.HTTP_404_NOT_FOUND: {"description": models.User.not_found_message(), 'model': NotFoundResponse}})
async def get_user_access_tokens(
        authorization: typing.Annotated[GetAuthorizationReturn, Depends(get_authorization())]) -> list[models.UserAccessToken]:
    with Session(c.db_engine) as session:
        user_access_tokens = await models.UserAccessToken.get_all_by_key_values(
            session, {'user_id': authorization.user.id})
        return user_access_tokens


@app.delete('/user-access-tokens/{user_access_token_id}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_access_token(
        user_access_token_id: models.UserAccessTokenTypes.id,
        authorization: typing.Annotated[GetAuthorizationReturn, Depends(get_authorization())]):

    with Session(c.db_engine) as session:
        user_access_token = await models.UserAccessToken.get(session, user_access_token_id)
        if user_access_token.user_id != authorization.user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=models.UserAccessToken.not_found_message())
        if await models.UserAccessToken.delete_one_by_id(session, user_access_token_id) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=models.UserAccessToken.not_found_message())
        return Response(status_code=status.HTTP_204_NO_CONTENT)

#
# API Keys
#


@app.get('/admin/api-keys/{api_key_id}', responses={status.HTTP_404_NOT_FOUND: {"description": models.ApiKey.not_found_message(), 'model': NotFoundResponse}})
async def get_api_key_by_id_admin(
    api_key_id: models.ApiKeyTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))]
) -> models.ApiKey:
    with Session(c.db_engine) as session:
        return await models.ApiKey.get(session, api_key_id)


@app.post('/admin/api-keys/', responses={status.HTTP_409_CONFLICT: {"description": 'User already exists', 'model': DetailOnlyResponse}})
async def post_api_key_admin(
    api_key_create_admin: models.ApiKeyCreateAdmin,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))]
) -> models.ApiKey:
    with Session(c.db_engine) as session:
        return await api_key_create_admin.post(session)


@ app.get('/api-keys/', responses={status.HTTP_404_NOT_FOUND: {"description": models.User.not_found_message(), 'model': NotFoundResponse}})
async def get_api_keys(
        authorization: typing.Annotated[GetAuthorizationReturn, Depends(get_authorization())]) -> list[models.ApiKey]:

    with Session(c.db_engine) as session:
        api_keys = await models.ApiKey.get_all_by_key_values(
            session, {'user_id': authorization.user.id})
        return api_keys


@app.post('/api-keys/')
async def post_api_key(
        api_key_create: models.ApiKeyCreate,
        authorization: typing.Annotated[GetAuthorizationReturn, Depends(get_authorization())]) -> models.ApiKey:

    api_key_admin_create = models.ApiKeyCreateAdmin(
        **api_key_create.model_dump(), user_id=authorization.user.id)

    with Session(c.db_engine) as session:
        return await api_key_admin_create.post(session)


@app.patch('/api-keys/{api_key_id}/')
async def patch_api_key(
        api_key_id: models.ApiKeyTypes.id,
        api_key_update: models.ApiKeyUpdate,
        authorization: typing.Annotated[GetAuthorizationReturn, Depends(get_authorization())]) -> models.ApiKey:

    with Session(c.db_engine) as session:

        api_key = await models.ApiKey.get(session, api_key_id)
        if api_key.user_id != authorization.user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=models.ApiKey.not_found_message())

        api_key.sqlmodel_update(api_key_update)
        await api_key.add_to_db(session)
        return api_key


@ app.delete('/api-keys/{api_key_id}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    api_key_id: models.ApiKeyTypes.id,
        authorization: typing.Annotated[GetAuthorizationReturn, Depends(get_authorization())]):
    with Session(c.db_engine) as session:

        api_key = await models.ApiKey.get(session, api_key_id)
        if api_key.user_id != authorization.user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=models.ApiKey.not_found_message())
        if await models.ApiKey.delete_one_by_id(session, api_key_id) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=models.ApiKey.not_found_message())
        return Response(status_code=status.HTTP_204_NO_CONTENT)


class ApiKeyJWTResponse(BaseModel):
    jwt: str


@app.get('/api-keys/{api_key_id}/generate-jwt/', responses={status.HTTP_404_NOT_FOUND: {"description": models.ApiKey.not_found_message(), 'model': NotFoundResponse}})
async def get_api_key_jwt(
    api_key_id: models.ApiKeyTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization())]
) -> ApiKeyJWTResponse:
    with Session(c.db_engine) as session:
        api_key = await models.ApiKey.get(session, api_key_id)
        if api_key.user_id != authorization.user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=models.ApiKey.not_found_message())

        return ApiKeyJWTResponse(
            jwt=jwt_encode(api_key.export_to_jwt())
        )


@app.post('/api-keys/{api_key_id}/scopes/{scope_id}/', status_code=status.HTTP_204_NO_CONTENT)
async def add_scope_to_api_key(
    api_key_id: models.ApiKeyTypes.id,
    scope_id: models.ScopeTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization())]
):

    with Session(c.db_engine) as session:
        api_key = await models.ApiKey.get(session, api_key_id)
        if api_key.user_id != authorization.user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=models.ApiKey.not_found_message())

        user = await models.User.get(session, authorization.user.id)

        # see if user is permitted to add this scope
        if scope_id not in c.user_role_id_scope_ids[user.user_role_id]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Scope doesn't exist for this user")

        existing_api_key_scope = await models.ApiKeyScope.get_one_by_id(session, (api_key_id, scope_id))
        if existing_api_key_scope:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Scope already exists for this API key")

        await models.ApiKeyScopeCreateAdmin(api_key_id=api_key_id, scope_id=scope_id).post(session)
        return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.delete('/api-keys/{api_key_id}/scopes/{scope_id}/', status_code=status.HTTP_204_NO_CONTENT)
async def remove_scope_from_api_key(
    api_key_id: models.ApiKeyTypes.id,
    scope_id: models.ScopeTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization())]
):
    with Session(c.db_engine) as session:
        api_key = await models.ApiKey.get(session, api_key_id)
        if api_key.user_id != authorization.user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=models.ApiKey.not_found_message())

        if await models.ApiKeyScope.delete(session, (api_key_id, scope_id)):
            return Response(status_code=status.HTTP_204_NO_CONTENT)

# galleries


@app.get('/admin/galleries/{gallery_id}', responses={status.HTTP_404_NOT_FOUND: {"description": models.Gallery.not_found_message(), 'model': NotFoundResponse}})
async def get_gallery_by_id_admin(
    gallery_id: models.GalleryTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))]
) -> models.Gallery:
    with Session(c.db_engine) as session:
        return await models.Gallery.get(session, gallery_id)


@app.post('/admin/galleries/', responses={status.HTTP_409_CONFLICT: {"description": 'Gallery already exists', 'model': DetailOnlyResponse}})
async def post_gallery_admin(
    gallery_create_admin: models.GalleryCreateAdmin,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))]
) -> models.Gallery:
    with Session(c.db_engine) as session:
        return await gallery_create_admin.post(session)


@app.patch('/admin/galleries/{gallery_id}/', responses={status.HTTP_404_NOT_FOUND: {"description": models.Gallery.not_found_message(), 'model': NotFoundResponse}})
async def patch_gallery_admin(
    gallery_id: models.GalleryTypes.id,
    gallery_update_admin: models.GalleryUpdateAdmin,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))]
) -> models.Gallery:

    if gallery_id != gallery_update_admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Gallery id in url does not match gallery id in body')

    with Session(c.db_engine) as session:
        return gallery_update_admin.patch(session)


@app.delete('/admin/galleries/{gallery_id}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_gallery_admin(
    gallery_id: models.GalleryTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))]
) -> Response:
    with Session(c.db_engine) as session:
        if models.Gallery.delete_one_by_id(session, gallery_id):
            return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get('/admin/galleries/available/')
async def get_is_gallery_available_admin(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))],
    gallery_available_admin: models.GalleryAvailableAdmin = Depends(),
) -> ItemAvailableResponse:
    with Session(c.db_engine) as session:
        return ItemAvailableResponse(available=await models.Gallery.is_available(session, gallery_available_admin))


@app.get('/galleries/available/')
async def get_is_gallery_available(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization())],
    gallery_available: models.GalleryAvailable = Depends(),
) -> ItemAvailableResponse:

    print(gallery_available.model_dump())

    with Session(c.db_engine) as session:
        return ItemAvailableResponse(available=await models.Gallery.is_available(session, models.GalleryAvailableAdmin(
            **gallery_available.model_dump(), user_id=authorization.user.id
        )))


@ app.get('/galleries/')
async def get_galleries(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization())]
) -> models.PluralGalleriesDict:

    with Session(c.db_engine) as session:

        galleries = await models.Gallery.get_all_by_key_values(
            session, {'user_id': authorization.user.id}
        )

        gallery_permissions = await models.GalleryPermission.get_all_by_key_values(
            session, {'user_id': authorization.user.id})

        galleries.append(
            await models.Gallery.get_all_by_key_values(
                session, {'id': [
                    gallery_permission.gallery_id for gallery_permission in gallery_permissions]}
            )
        )

        return {
            gallery.id: gallery for gallery in galleries
        }


@ app.get('/galleries/{gallery_id}', responses={status.HTTP_404_NOT_FOUND: {"description": models.Gallery.not_found_message(), 'model': NotFoundResponse}})
async def get_gallery(
    gallery_id: models.GalleryTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(raise_exceptions=False))]
) -> models.GalleryPublic:
    with Session(c.db_engine) as session:
        gallery = await models.Gallery.get(session, gallery_id)

        if gallery.visibility_level == c.visibility_level_name_mapping['private']:
            if authorization.exception:
                raise HTTPException(status.HTTP_404_NOT_FOUND,
                                    detail=models.Gallery.not_found_message())

            if gallery.user_id != authorization.user.id:
                gallery_permission = await models.GalleryPermission.get(
                    session, (gallery_id, authorization.user.id))

                if not gallery_permission:
                    raise HTTPException(status.HTTP_404_NOT_FOUND,
                                        detail=models.Gallery.not_found_message())

        return models.GalleryPublic.model_validate(gallery)


@ app.post('/galleries/', responses={status.HTTP_409_CONFLICT: {"description": models.Gallery.already_exists_message(), 'model': DetailOnlyResponse}})
async def post_gallery(gallery_create: models.GalleryCreate,
                       authorization: typing.Annotated[GetAuthorizationReturn, Depends(
                           get_authorization())]
                       ) -> models.GalleryPrivate:

    gallery_create_admin = models.GalleryCreateAdmin(
        **gallery_create.model_dump())

    with Session(c.db_engine) as session:
        gallery = await gallery_create_admin.post(session)
        return models.GalleryPrivate.model_validate(gallery)


@ app.patch('/galleries/{gallery_id}/', responses={
    status.HTTP_403_FORBIDDEN: {"description": 'User does not have permission to update this gallery', 'model': DetailOnlyResponse},
    status.HTTP_404_NOT_FOUND: {"description": models.Gallery.not_found_message(), 'model': NotFoundResponse},
    status.HTTP_409_CONFLICT: {"description": models.Gallery.already_exists_message(), 'model': DetailOnlyResponse}}
)
async def patch_gallery(gallery_id: models.GalleryTypes.id, gallery_update: models.GalleryUpdate,
                        authorization: typing.Annotated[GetAuthorizationReturn, Depends(
                            get_authorization())]
                        ) -> models.Gallery:

    with Session(c.db_engine) as session:

        gallery = await models.Gallery.get(session, gallery_id)
        if not gallery:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail=models.Gallery.not_found_message())

        gallery_permission = await models.GalleryPermission.get(
            session, (gallery_id, authorization.user.id))

        if not gallery_permission and gallery.visibility_level == c.visibility_level_name_mapping['private']:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail=models.Gallery.not_found_message())
        if gallery_permission.permission_level < c.permission_level_name_mapping['editor']:
            raise HTTPException(status.HTTP_403_FORBIDDEN,
                                detail='User does not have permission to update this gallery')

        gallery.sqlmodel_update(gallery_update.model_dump(exclude_unset=True))
        await gallery.add_to_db(session)
        return gallery


@ app.delete('/galleries/{gallery_id}/', status_code=status.HTTP_204_NO_CONTENT, responses={
    status.HTTP_403_FORBIDDEN: {"description": 'User does not have permission to delete this gallery', 'model': DetailOnlyResponse},
    status.HTTP_404_NOT_FOUND: {
        "description": models.Gallery.not_found_message(), 'model': NotFoundResponse}
}
)
async def delete_gallery(gallery_id: models.GalleryTypes.id,
                         authorization: typing.Annotated[GetAuthorizationReturn, Depends(
                             get_authorization())]
                         ) -> Response:
    with Session(c.db_engine) as session:
        gallery = await models.Gallery.get(session, gallery_id)
        if not gallery:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail=models.Gallery.not_found_message())

        gallery_permission = await models.GalleryPermission.get(
            session, (gallery_id, authorization.user.id))

        if not gallery_permission:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail=models.Gallery.not_found_message())
        if gallery_permission.permission_level < c.permission_level_name_mapping['owner']:
            raise HTTPException(status.HTTP_403_FORBIDDEN,
                                detail='User does not have permission to delete this gallery')
        if models.Gallery.delete_one_by_id(session, gallery_id) == 0:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail=models.Gallery.not_found_message())

        shutil.rmtree(gallery.get_dir(c.galleries_dir))

        return Response(status_code=status.HTTP_204_NO_CONTENT)


class UploadFileToGalleryResponse(BaseModel):
    message: str


@ app.post("/galleries/{gallery_id}/upload/", status_code=status.HTTP_201_CREATED)
async def upload_file_to_gallery(
    gallery_id: models.GalleryTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization())],
    file: UploadFile = File(...)
) -> UploadFileToGalleryResponse:

    with Session(c.db_engine) as session:
        gallery = await models.Gallery.get(session, gallery_id)
        if not gallery:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail=models.Gallery.not_found_message())

        gallery_permission = await models.GalleryPermission.get(
            session, (gallery_id, authorization.user.id))

        if not gallery_permission:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail=models.Gallery.not_found_message())
        if gallery_permission.permission_level < c.permission_level_name_mapping['editor']:
            raise HTTPException(status.HTTP_403_FORBIDDEN,
                                detail='User does not have permission to add files to this gallery')

        print(file.__dict__)
        file_path = gallery.get_dir(c.galleries_dir) / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    return UploadFileToGalleryResponse(message="Files uploaded successfully")

# Pages


class GetProfilePageResponse(GetAuthReturn):
    user: models.UserPrivate | None = None


@ app.get('/profile/page/')
async def get_pages_profile(authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization())]) -> GetProfilePageResponse:

    with Session(c.db_engine) as session:
        user = await models.User.get_one_by_id(session, authorization.user.id)
        if user is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail=models.User.not_found_message())

        return GetProfilePageResponse(
            **get_auth(authorization).model_dump(),
            user=models.UserPrivate.model_validate(user)
        )


class GetHomePageResponse(GetAuthReturn):
    pass


@ app.get('/home/page/')
async def get_home_page(authorization: typing.Annotated[GetAuthorizationReturn, Depends(get_authorization(raise_exceptions=False))]) -> GetHomePageResponse:

    return GetHomePageResponse(
        **get_auth(authorization).model_dump()
    )


class GetSettingsPageResponse(GetAuthReturn):
    pass


@ app.get('/settings/page/')
async def get_settings_page(authorization: typing.Annotated[GetAuthorizationReturn, Depends(get_authorization(raise_exceptions=False))]) -> GetSettingsPageResponse:
    return GetSettingsPageResponse(
        **get_auth(authorization).model_dump()
    )


class GetSettingsApiKeysPageResponse(GetAuthReturn):
    api_keys: models.PluralApiKeysDict
    api_key_scope_ids: dict[models.ApiKeyTypes.id, list[models.ScopeTypes.id]]


@ app.get('/settings/api-keys/page/')
async def get_settings_page(
        authorization: typing.Annotated[GetAuthorizationReturn, Depends(get_authorization())]) -> GetSettingsApiKeysPageResponse:

    with Session(c.db_engine) as session:

        user = await models.User.get(session, authorization.user.id)
        api_keys = user.api_keys

        return GetSettingsApiKeysPageResponse(
            **get_auth(authorization).model_dump(),
            api_keys=models.ApiKey.export_plural_to_dict(api_keys),
            api_key_scope_ids={
                api_key.id: await api_key.get_scope_ids() for api_key in api_keys}
        )


class GetStylesPageResponse(GetAuthReturn):
    pass


@ app.get('/styles/page/')
async def get_styles_page(authorization: typing.Annotated[GetAuthorizationReturn, Depends(get_authorization(raise_exceptions=False))]) -> GetStylesPageResponse:
    return GetStylesPageResponse(
        **get_auth(authorization).model_dump()
    )


class GetGalleryPageResponse(GetAuthReturn):
    gallery: models.GalleryPublic
    gallery_permissions: dict[models.GalleryTypes.id, models.GalleryPermission]


@ app.get('/galleries/{gallery_id}/page/', responses={status.HTTP_404_NOT_FOUND: {"description": models.Gallery.not_found_message(), 'model': NotFoundResponse}})
async def get_gallery_page(
    gallery_id: models.GalleryTypes.id | None,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(raise_exceptions=False))]
) -> GetGalleryPageResponse:

    gallery = await get_gallery(gallery_id, authorization)
    return GetGalleryPageResponse(
        **get_auth(authorization).model_dump(),
        gallery=models.GalleryPublic.model_validate(gallery)
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
