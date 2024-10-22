import uvicorn
from fastapi import FastAPI, HTTPException, Query, status, Response, Depends, Request, BackgroundTasks, Form
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

from google.oauth2 import id_token
from google.auth.transport import requests


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('startingup')
    yield
    print('closingdown')

app = FastAPI(lifespan=lifespan)
c = get_client()


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
            c.root_config['cookie_keys']['access_token'])
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


class GetAuthorizationReturn(BaseModel):
    isAuthorized: bool = False
    expiry: datetime.datetime | None = None
    exception: auth.EXCEPTION | None = None
    user: models.UserPrivate | None = None
    scopes: set[models.ScopeTypes.name] | None = None
    auth_credential: models.AUTH_CREDENTIAL_MODEL | None = None


def get_authorization(
    required_scopes: set[models.ScopeTypes.name] = set(),
    raise_exceptions: bool = True,
    permitted_auth_credential_types: set[models.AuthCredentialTypes.type] = set(
        key for key in models.AUTH_CREDENTIAL_MODEL_MAPPING),
    override_lifetime: datetime.timedelta | None = None,
    remove_cookie_on_exception: bool = True,
) -> typing.Callable[[str], GetAuthorizationReturn]:

    async def dependecy(auth_token: typing.Annotated[str | None, Depends(oauth2_scheme)], response: Response) -> GetAuthorizationReturn:
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

                scopes = await auth_credential.get_scopes()
                scope_names: set[models.ScopeTypes.name] = {
                    scope.name for scope in scopes}

                if not required_scopes.issubset(scope_names):
                    if raise_exceptions:
                        raise auth.not_permitted_exception()
                    return GetAuthorizationReturn(exception='not_permitted')

                return GetAuthorizationReturn(
                    isAuthorized=True,
                    expiry=dt_exp,
                    user=models.UserPrivate.model_validate(user),
                    scopes=scope_names,
                    auth_credential=auth_credential,
                )

        inner_response = await inner()
        if inner_response.exception and raise_exceptions:
            exception_to_raise = auth.EXCEPTION_MAPPING[inner_response.exception]
            if remove_cookie_on_exception and exception_to_raise.status_code in {status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED, status.HTTP_404_NOT_FOUND}:
                delete_access_token_cookie(response)

            if raise_exceptions:
                raise exception_to_raise

        return inner_response

    return dependecy


class GetAuthBaseReturn(BaseModel):
    user: models.UserPrivate | None = None
    scopes: set[models.ScopeTypes.name] | None = None
    expiry: models.AuthCredentialTypes.expiry | None = None


assert c.root_config['auth_key'] == 'auth'


class GetAuthReturn(BaseModel):
    auth: GetAuthBaseReturn


def get_auth(get_authorization_return: GetAuthorizationReturn) -> GetAuthReturn:
    return GetAuthReturn(auth=GetAuthBaseReturn(
        user=get_authorization_return.user,
        scopes=get_authorization_return.scopes,
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


def set_access_token_cookie(access_token: str, response: Response, stay_signed_in: bool):

    kwargs = {}
    if stay_signed_in:
        kwargs['expires'] = datetime.datetime.now(
            datetime.UTC) + c.authentication['default_expiry_timedelta']

    response.set_cookie(
        key=c.root_config['cookie_keys']['access_token'],
        value=access_token,
        httponly=True,
        secure=True,
        samesite="Lax",
        **kwargs
    )


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

    print(user)
    print(stay_signed_in)

    with Session(c.db_engine) as session:

        user_access_token = await models.UserAccessTokenCreateAdmin(
            user_id=user.id, lifespan=c.authentication['default_expiry_timedelta']).create()
        await user_access_token.add_to_db(session)
        set_access_token_cookie(jwt_encode(
            user_access_token.export_to_jwt()), response, stay_signed_in)

        return LoginResponse(
            auth=GetAuthBaseReturn(
                user=models.UserPrivate.model_validate(user),
                scopes=set(
                    [scope.name for scope in await user_access_token.get_scopes()]),
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

    user_create_admin = models.UserCreateAdmin(email=email, password=password)

    with Session(c.db_engine) as session:
        user = await user_create_admin.post(session)

        user_access_token = await models.UserAccessTokenCreateAdmin(
            user_id=user.id, type='access_token', lifespan=c.authentication['default_expiry_timedelta']).create()
        await user_access_token.add_to_db(session)
        set_access_token_cookie(jwt_encode(
            user_access_token.export_to_jwt()), response, stay_signed_in)

        return SignupResponse(
            auth=GetAuthBaseReturn(
                user=models.UserPrivate.model_validate(user),
                scopes=set(
                    [scope.name for scope in await user_access_token.get_scopes()]),
                expiry=user_access_token.expiry
            )
        )


class LoginWithEmailMagicLinkRequest(BaseModel):
    email: models.UserTypes.email


async def send_magic_link_to_email(model: LoginWithEmailMagicLinkRequest):

    with Session(c.db_engine) as session:
        user = await models.User.get_one_by_key_values(
            session, {'email': model.email})

        if user:
            user_access_token = await models.UserAccessTokenCreateAdmin(
                user_id=user.id, lifespan=c.authentication['magic_link_expiry_timedelta']).create()
            await user_access_token.add_to_db(session)

            print('beep boop beep... sending email')
            print('http://localhost:3000' +
                  c.root_config['magic_link_frontend_url'] + '?access_token=' + jwt_encode(user_access_token.export_to_jwt()))

    # still need to fill this function in!


@ app.post('/auth/login/email-magic-link/')
async def login_with_email_magic_link(model: LoginWithEmailMagicLinkRequest, background_tasks: BackgroundTasks) -> DetailOnlyResponse:
    background_tasks.add_task(send_magic_link_to_email, model)
    return DetailOnlyResponse(detail='If an account with this email exists, a login link has been sent.')


class VerifyMagicLinkRequest(GetAuthReturn):
    pass


@ app.post('/auth/verify-magic-link/', responses={status.HTTP_401_UNAUTHORIZED: {'description': 'Invalid token', 'model': DetailOnlyResponse}})
async def verify_magic_link(authorization: typing.Annotated[GetAuthorizationReturn, Depends(get_authorization(permitted_auth_credential_types={'access_token'},
                                                                                                              raise_exceptions=True, override_lifetime=c.authentication['magic_link_expiry_timedelta']))], response: Response) -> VerifyMagicLinkRequest:

    with Session(c.db_engine) as session:

        user_access_token = await models.UserAccessTokenCreateAdmin(
            user_id=authorization.user.id, lifespan=c.authentication['default_expiry_timedelta']).create()
        await user_access_token.add_to_db(session)
        set_access_token_cookie(jwt_encode(
            user_access_token.export_to_jwt()), response)

        # one time link, delete the auth_credential
        await models.UserAccessToken.delete_one_by_id(
            session, authorization.auth_credential.id)

        return VerifyMagicLinkRequest(
            auth=GetAuthBaseReturn(
                user=models.UserPrivate.model_validate(authorization.user),
                scopes=set(
                    [scope.name for scope in await user_access_token.get_scopes()]),
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

        return VerifyMagicLinkRequest(
            auth=GetAuthBaseReturn(
                user=models.UserPrivate.model_validate(user),
                scopes=set(
                    [scope.name for scope in await user_access_token.get_scopes()]),
                expiry=user_access_token.expiry
            )
        )


def delete_access_token_cookie(response: Response):
    response.delete_cookie(c.root_config['cookie_keys']['access_token'])


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
        get_authorization(raise_exceptions=True, required_scopes={models.ScopeNames.ADMIN}))]
) -> models.User:
    with Session(c.db_engine) as session:
        return await models.User.get(session, user_id)


@app.post('/admin/users/', responses={status.HTTP_409_CONFLICT: {"description": 'User already exists', 'model': DetailOnlyResponse}})
async def post_user_admin(
    user_create: models.UserCreateAdmin,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(raise_exceptions=True, required_scopes={models.ScopeNames.ADMIN}))]
) -> models.User:
    with Session(c.db_engine) as session:
        return await user_create.post(session)


@app.patch('/admin/users/{user_id}/', responses={status.HTTP_400_BAD_REQUEST: {"description": 'User id in url does not match user id in body'}})
async def patch_user_admin(
    user_id: models.UserTypes.id,
    user_update_admin: models.UserUpdateAdmin,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(raise_exceptions=True, required_scopes={models.ScopeNames.ADMIN}))]
) -> models.User:

    if user_id != user_update_admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='User id in url does not match user id in body')

    with Session(c.db_engine) as session:
        return user_update_admin.patch(session)


@app.delete('/admin/users/{user_id}/', status_code=204, responses={})
async def delete_user_admin(
    user_id: models.UserTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(raise_exceptions=True, required_scopes={models.ScopeNames.ADMIN}))]
):
    with Session(c.db_engine) as session:
        if await models.User.delete(session, user_id):
            return Response(status_code=204)


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


@ app.delete('/user/', status_code=204, responses={
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
            return Response(status_code=204)

#
# User Access Tokens
#


@app.get('/admin/user-access-tokens/{user_access_token_id}', responses={status.HTTP_404_NOT_FOUND: {"description": models.UserAccessToken.not_found_message(), 'model': NotFoundResponse}})
async def get_user_access_token_by_id_admin(
    user_access_token_id: models.UserAccessTokenTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(raise_exceptions=True, required_scopes={models.ScopeNames.ADMIN}))]
) -> models.UserAccessToken:
    with Session(c.db_engine) as session:
        return await models.UserAccessToken.get(session, user_access_token_id)


@app.post('/admin/user-access-tokens/', responses={status.HTTP_409_CONFLICT: {"description": 'User already exists', 'model': DetailOnlyResponse}})
async def post_user_access_token_admin(
    user_access_token_create_admin: models.UserAccessTokenCreateAdmin,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(raise_exceptions=True, required_scopes={models.ScopeNames.ADMIN}))]
) -> models.UserAccessToken:
    with Session(c.db_engine) as session:
        return user_access_token_create_admin.post(session)


@app.patch('/admin/user-access-tokens/{user_access_token_id}/', responses={status.HTTP_400_BAD_REQUEST: {"description": 'User access token id in url does not match user access token id in body'}})
async def patch_user_access_token_admin(
    user_access_token_id: models.UserAccessTokenTypes.id,
    user_access_token_update_admin: models.UserAccessTokenUpdateAdmin,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(raise_exceptions=True, required_scopes={models.ScopeNames.ADMIN}))]
) -> models.User:

    if user_access_token_id != user_access_token_update_admin._id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='User access token id in url does not match user access token id in body')

    with Session(c.db_engine) as session:
        return user_access_token_update_admin.patch(session)


@app.delete('/admin/user-access-tokens/{user_access_token_id}/', status_code=204, responses={status.HTTP_404_NOT_FOUND: {"description": models.UserAccessToken.not_found_message(), 'model': NotFoundResponse}})
async def delete_user_admin(
    user_access_token_id: models.UserAccessTokenTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(raise_exceptions=True, required_scopes={models.ScopeNames.ADMIN}))]
):
    with Session(c.db_engine) as session:
        if models.UserAccessToken.delete(session, user_access_token_id):
            return Response(status_code=204)


@ app.get('/user-access-tokens/', responses={status.HTTP_404_NOT_FOUND: {"description": models.User.not_found_message(), 'model': NotFoundResponse}})
async def get_user_access_tokens(
        authorization: typing.Annotated[GetAuthorizationReturn, Depends(get_authorization())]) -> list[models.UserAccessToken]:
    with Session(c.db_engine) as session:
        user_access_tokens = await models.UserAccessToken.get_all_by_key_values(
            session, {'user_id': authorization.user.id})
        return user_access_tokens


@app.delete('/user-access-tokens/{user_access_token_id}/', status_code=204)
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
        return Response(status_code=204)

#
# API Keys
#


@app.get('/admin/api-keys/{api_key_id}', responses={status.HTTP_404_NOT_FOUND: {"description": models.APIKey.not_found_message(), 'model': NotFoundResponse}})
async def get_api_key_by_id_admin(
    api_key_id: models.APIKeyTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(raise_exceptions=True, required_scopes={models.ScopeNames.ADMIN}))]
) -> models.APIKey:
    with Session(c.db_engine) as session:
        return await models.APIKey.get(session, api_key_id)


@app.post('/admin/api-keys/', responses={status.HTTP_409_CONFLICT: {"description": 'User already exists', 'model': DetailOnlyResponse}})
async def post_api_key_admin(
    api_key_create_admin: models.APIKeyCreateAdmin,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(raise_exceptions=True, required_scopes={models.ScopeNames.ADMIN}))]
) -> models.APIKey:
    with Session(c.db_engine) as session:
        return await api_key_create_admin.post(session)


@ app.get('/api-keys/', responses={status.HTTP_404_NOT_FOUND: {"description": models.User.not_found_message(), 'model': NotFoundResponse}})
async def get_api_keys(
        authorization: typing.Annotated[GetAuthorizationReturn, Depends(get_authorization())]) -> list[models.APIKey]:

    with Session(c.db_engine) as session:
        api_keys = await models.APIKey.get_all_by_key_values(
            session, {'user_id': authorization.user.id})
        return api_keys


@app.post('/api-keys/')
async def post_api_key(
        api_key_create: models.APIKeyCreate,
        authorization: typing.Annotated[GetAuthorizationReturn, Depends(get_authorization())]) -> models.APIKey:

    api_key_admin_create = models.APIKeyCreateAdmin(
        **api_key_create.model_dump(), user_id=authorization.user.id)

    with Session(c.db_engine) as session:
        return await api_key_admin_create.post(session)


@app.patch('/api-keys/{api_key_id}/')
async def patch_api_key(
        api_key_id: models.APIKeyTypes.id,
        api_key_update: models.APIKeyUpdate,
        authorization: typing.Annotated[GetAuthorizationReturn, Depends(get_authorization())]) -> models.APIKey:

    with Session(c.db_engine) as session:

        api_key = await models.APIKey.get(session, api_key_id)
        if api_key.user_id != authorization.user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=models.APIKey.not_found_message())

        api_key.sqlmodel_update(api_key_update)
        await api_key.add_to_db(session)
        return api_key


@ app.delete('/api-keys/{api_key_id}/', status_code=204)
async def delete_api_key(
    api_key_id: models.APIKeyTypes.id,
        authorization: typing.Annotated[GetAuthorizationReturn, Depends(get_authorization())]):
    with Session(c.db_engine) as session:

        api_key = await models.APIKey.get(session, api_key_id)
        if api_key.user_id != authorization.user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=models.APIKey.not_found_message())
        if await models.APIKey.delete_one_by_id(session, api_key_id) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=models.APIKey.not_found_message())
        return Response(status_code=204)

    # # Gallery
    # async def get_gallery_available_params(
    #     name: models.GalleryTypes.name,
    #     parent_id: models.GalleryTypes.parent_id = None,
    #     date: models.GalleryTypes.date = None
    # ) -> models.GalleryAvailable:
    #     return models.GalleryAvailable(name=name, parent_id=parent_id, date=date)
    # @ app.get('/galleries/available/')
    # async def get_gallery_available(
    #     token_return: typing.Annotated[GetTokenReturn, Depends(get_token)],
    #     gallery_available: models.GalleryAvailable = Depends(
    #         get_gallery_available_params)
    # ) -> ItemAvailableResponse:
    #     auth_return = await get_auth(token_return)
    #     if auth_return.exception:
    #         raise auth.EXCEPTION_MAPPING[auth_return.exception]
    #     with Session(c.db_engine) as session:
    #         # Check if the gallery name, parent_id, and date all exist already
    #         return ItemAvailableResponse(available=await models.Gallery.is_available(session, gallery_available))
    # @app.get('/galleries/{gallery_id}/', responses={status.HTTP_404_NOT_FOUND: {"description": models.Gallery.not_found_message(), 'model': NotFoundResponse}})
    # async def get_gallery(gallery_id: models.GalleryTypes.id, token_return: typing.Annotated[GetTokenReturn, Depends(get_token)]) -> models.Gallery:
    #     auth_return = await get_auth(token_return)
    #     if auth_return.exception:
    #         raise auth.EXCEPTION_MAPPING[auth_return.exception]
    #     with Session(c.db_engine) as session:
    #         gallery = models.Gallery.get_one_by_id(session, gallery_id)
    #         if not gallery:
    #             raise HTTPException(status.HTTP_404_NOT_FOUND,
    #                                 detail=models.Gallery.not_found_message())
    #         if gallery.visibility == models.VisibilityLevel.PRIVATE:
    #             gallery_permission = models.GalleryPermission.get_one_by_id(
    #                 session, (gallery_id, auth_return.user.id))
    #             if not gallery_permission:
    #                 raise HTTPException(status.HTTP_404_NOT_FOUND,
    #                                     detail=models.Gallery.not_found_message())
    #         return gallery
    # @ app.post('/galleries/', responses={status.HTTP_409_CONFLICT: {"description": 'Gallery already exists', 'model': DetailOnlyResponse}})
    # async def post_gallery(gallery_create: models.GalleryCreate, token_return: typing.Annotated[GetTokenReturn, Depends(get_token)]) -> models.Gallery:
    #     auth_return = await get_auth(token_return)
    #     if auth_return.exception:
    #         raise auth.EXCEPTION_MAPPING[auth_return.exception]
    #     with Session(c.db_engine) as session:
    #         if not await models.Gallery.is_available(session, models.GalleryAvailable.model_validate(gallery_create)):
    #             raise HTTPException(
    #                 status_code=status.HTTP_409_CONFLICT, detail='Gallery already exists')
    #         gallery = gallery_create.create()
    #         gallery.add_to_db(session)
    #         gallery_permission = models.GalleryPermission(
    #             gallery_id=gallery.id, user_id=auth_return.user.id, permission_level=models.PermissionLevel.OWNER)
    #         gallery_permission.add_to_db(session)
    #         return models.Gallery.model_validate(gallery)
    # @app.patch('/galleries/{gallery_id}/', responses={
    #     status.HTTP_401_UNAUTHORIZED: {'description': 'Invalid token', 'model': DetailOnlyResponse},
    #     status.HTTP_403_FORBIDDEN: {"description": 'User does not have permission to update this gallery', 'model': DetailOnlyResponse},
    #     status.HTTP_404_NOT_FOUND: {"description": models.Gallery.not_found_message(), 'model': NotFoundResponse},
    #     status.HTTP_409_CONFLICT: {"description": 'Gallery already exists', 'model': DetailOnlyResponse}, }
    # )
    # async def patch_gallery(gallery_id: models.GalleryTypes.id, gallery_update: models.GalleryUpdate, token_return: typing.Annotated[GetTokenReturn, Depends(get_token)]) -> models.Gallery:
    #     auth_return = await get_auth(token_return)
    #     if auth_return.exception:
    #         raise auth.EXCEPTION_MAPPING[auth_return.exception]
    #     with Session(c.db_engine) as session:
    #         gallery = models.Gallery.get_one_by_id(session, gallery_id)
    #         if not gallery:
    #             raise HTTPException(status.HTTP_404_NOT_FOUND,
    #                                 detail=models.Gallery.not_found_message())
    #         gallery_permission = models.GalleryPermission.get_one_by_id(
    #             session, (gallery_id, auth_return.user.id))
    #         if not gallery_permission and gallery.visibility == models.VisibilityLevel.PRIVATE:
    #             raise HTTPException(status.HTTP_404_NOT_FOUND,
    #                                 detail=models.Gallery.not_found_message())
    #         if gallery_permission.permission_level < models.PermissionLevel.EDITOR:
    #             raise HTTPException(status.HTTP_403_FORBIDDEN,
    #                                 detail='User does not have permission to update this gallery')
    #         response = await get_gallery_available(token_return, name=gallery_update.name, parent_id=gallery_update.parent_id, date=gallery_update.date)
    #         if response.available == False:
    #             raise HTTPException(
    #                 status_code=status.HTTP_409_CONFLICT, detail='Gallery already exists')
    #         gallery.sqlmodel_update(gallery_update)
    # @app.delete('/galleries/{gallery_id}/', status_code=204, responses={
    #     status.HTTP_403_FORBIDDEN: {"description": 'User does not have permission to delete this gallery', 'model': DetailOnlyResponse},
    #     status.HTTP_404_NOT_FOUND: {
    #         "description": models.Gallery.not_found_message(), 'model': NotFoundResponse}
    # }
    # )
    # async def delete_gallery(gallery_id: models.GalleryTypes.id, token_return: typing.Annotated[GetTokenReturn, Depends(get_token)]) -> Response:
    #     auth_return = await get_auth(token_return)
    #     if auth_return.exception:
    #         raise auth.EXCEPTION_MAPPING[auth_return.exception]
    #     with Session(c.db_engine) as session:
    #         gallery_permission = models.GalleryPermission.get_one_by_id(
    #             session, (gallery_id, auth_return.user.id))
    #         if not gallery_permission:
    #             raise HTTPException(status.HTTP_404_NOT_FOUND,
    #                                 detail=models.Gallery.not_found_message())
    #         if gallery_permission.permission_level < models.PermissionLevel.OWNER:
    #             raise HTTPException(status.HTTP_403_FORBIDDEN,
    #                                 detail='User does not have permission to delete this gallery')
    #         if models.Gallery.delete_one_by_id(session, gallery_id) == 0:
    #             raise HTTPException(status.HTTP_404_NOT_FOUND,
    #                                 detail=models.Gallery.not_found_message())
    #         return Response(status_code=204)
    # Page


class GetProfilePageResponse(GetAuthReturn):
    user: models.UserPrivate | None = None


@ app.get('/profile/page/')
async def get_pages_profile(authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(raise_exceptions=True))]) -> GetProfilePageResponse:

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


# class GetGalleryPageResponse(AuthResponse):
#     gallery: models.Gallery
#     gallery_permission: models.GalleryPermission | None = None
# @app.get('/galleries/{gallery_id}/page/')
# async def get_gallery_page(gallery_id: models.GalleryTypes.id, token_return: typing.Annotated[GetTokenReturn, Depends(get_token)]) -> GetGalleryPageResponse:
#     auth_return = await get_auth(token_return)
#     with Session(c.db_engine) as session:
#         gallery = models.Gallery.get_one_by_id(session, gallery_id)
#         if not gallery:
#             raise HTTPException(status.HTTP_404_NOT_FOUND,
#                                 detail=models.Gallery.not_found_message())
#         gallery_permission = models.GalleryPermission.get_one_by_id(
#             session, (gallery_id, auth_return.user.id))
#         if gallery.visibility == models.VisibilityLevel.PRIVATE:
#             if auth_return.exception:
#                 raise auth.EXCEPTION_MAPPING[auth_return.exception]
#             if not gallery_permission:
#                 raise HTTPException(status.HTTP_404_NOT_FOUND,
#                                     detail=models.Gallery.not_found_message())
#         return GetGalleryPageResponse(
#             auth=auth_return,
#             gallery=gallery,
#             gallery_permission=gallery_permission
#         )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
