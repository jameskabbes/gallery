import uvicorn
from fastapi import FastAPI, HTTPException, Query, status, Response, Depends, Request, BackgroundTasks, Form, File, UploadFile, APIRouter
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2, OAuth2PasswordRequestForm, OAuth2PasswordBearer, APIKeyHeader
from fastapi.security.utils import get_authorization_scheme_param
from contextlib import asynccontextmanager
from sqlalchemy.orm import selectinload
from gallery import get_client, models, utils, auth, client
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
    tokenUrl="auth/token/")


class DetailOnlyResponse(BaseModel):
    detail: str


class NotFoundResponse(DetailOnlyResponse):
    pass


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):

    response = JSONResponse(status_code=exc.status_code,
                            content={"detail": exc.detail}, headers=exc.headers)

    # in get_auhorization, a special header 'X-Auth-Error' is set, signaling the user should be logged out
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


class GetAuthorizationKwargs(typing.TypedDict, total=False):
    required_scopes: typing.Optional[set[client.ScopeTypes.name]]
    raise_exceptions: typing.Optional[bool]
    permitted_auth_credential_types: typing.Optional[set[models.AuthCredentialTypes.type]]
    override_lifetime: typing.Optional[datetime.timedelta]


class GetAuthorizationReturn(BaseModel):
    isAuthorized: bool = False
    expiry: typing.Optional[datetime.datetime] = None
    exception: typing.Optional[auth.EXCEPTION] = None
    user: typing.Optional[models.UserPrivate] = None
    scope_ids: typing.Optional[set[client.ScopeTypes.id]] = None
    auth_credential: typing.Optional[models.AUTH_CREDENTIAL_MODEL] = None

    @property
    def _user_id(self):
        if self.auth_credential:
            if self.auth_credential.user:
                return self.auth_credential.user._id
        else:
            return None


def get_authorization(
    **kwargs: typing.Unpack[GetAuthorizationKwargs]
) -> typing.Callable[[str], GetAuthorizationReturn]:

    required_scopes = kwargs.get('required_scopes', set())
    raise_exceptions = kwargs.get('raise_exceptions', True)
    permitted_auth_credential_types = kwargs.get('permitted_auth_credential_types', set(
        key for key in models.AUTH_CREDENTIAL_MODEL_MAPPING))
    override_lifetime = kwargs.get('override_lifetime', None)

    async def dependecy(response: Response, auth_token: typing.Annotated[str | None, Depends(oauth2_scheme)]) -> GetAuthorizationReturn:
        async def inner() -> GetAuthorizationReturn:
            # attempt to decode the jwt

            if auth_token == None:
                return GetAuthorizationReturn(exception='improper_format')

            try:
                payload: models.AuthCredential.JwtExport = jwt_decode(
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
                    session.delete(auth_credential)
                    session.commit()
                    return GetAuthorizationReturn(exception='authorization_expired')

                # if there was an overriden lifetime, check if it has expired
                if override_lifetime != None:
                    # take the minimum of the hardcoded jwt and database value, ### note: redundancy needed or not?

                    dt_ait_jwt = datetime.datetime.fromtimestamp(
                        payload['iat'], datetime.UTC)
                    dt_ait_db = auth_credential.issued.replace(
                        tzinfo=datetime.UTC)

                    if dt_now > (min(dt_ait_jwt, dt_ait_db) + override_lifetime):
                        session.delete(auth_credential)
                        session.commit()
                        return GetAuthorizationReturn(exception='authorization_expired')

                user = auth_credential.user
                if user == None:
                    return GetAuthorizationReturn(exception='user_not_found')

                # get the scopes for the user
                scope_ids: set[client.ScopeTypes.id] = set()

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
            if raise_exceptions:
                raise auth.EXCEPTION_MAPPING[inner_response.exception]

        return inner_response

    return dependecy


class AuthCredentialIdAndType(BaseModel):
    id: models.ApiKeyTypes.id | models.UserAccessTokenTypes.id
    type: models.AuthCredentialTypes.type


class GetAuthBaseReturn(BaseModel):
    user: typing.Optional[models.UserPrivate]
    scope_ids: typing.Optional[set[client.ScopeTypes.id]]
    expiry: typing.Optional[models.AuthCredentialTypes.expiry]
    auth_credential: typing.Optional[AuthCredentialIdAndType]


assert c.auth_key == 'auth'


class GetAuthReturn(BaseModel):
    auth: GetAuthBaseReturn


def get_auth(get_authorization_return: GetAuthorizationReturn) -> GetAuthReturn:
    return GetAuthReturn(auth=GetAuthBaseReturn(
        user=get_authorization_return.user,
        scope_ids=get_authorization_return.scope_ids,
        expiry=get_authorization_return.expiry,
        auth_credential=AuthCredentialIdAndType(id=get_authorization_return.auth_credential.id,
                                                type=get_authorization_return.auth_credential.type) if get_authorization_return.auth_credential else None
    ))


auth_router = APIRouter(prefix='/auth', tags=['Auth'])


@ auth_router.get('/')
async def auth_root(authorization: typing.Annotated[GetAuthorizationReturn, Depends(get_authorization(raise_exceptions=False))]) -> GetAuthReturn:
    return get_auth(authorization)


async def authenticate_user_with_username_and_password(form_data: typing.Annotated[OAuth2PasswordRequestForm, Depends()]) -> models.User:
    with Session(c.db_engine) as session:
        user = await models.User.authenticate(
            session, form_data.username, form_data.password)
        if not user:
            raise auth.EXCEPTION_MAPPING['credentials']
        return user


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


@ auth_router.post('/token/')
async def post_token(
    user: typing.Annotated[models.User, Depends(authenticate_user_with_username_and_password)],
    response: Response,
    stay_signed_in: bool = Form(c.authentication['stay_signed_in_default'])
) -> TokenResponse:
    with Session(c.db_engine) as session:
        user_access_token = await models.UserAccessToken.api_post(
            session=session, c=c, authorized_user_id=user.id, admin=False, create_model=models.UserAccessTokenCreateAdmin(
                user_id=user.id, lifespan=c.authentication['default_expiry_timedelta']
            ))

        encoded_jwt = jwt_encode(
            user_access_token.export_to_jwt())

        set_access_token_cookie(encoded_jwt, response, stay_signed_in)
        return TokenResponse(access_token=encoded_jwt, token_type='bearer')


class LoginResponse(GetAuthReturn):
    pass


@ auth_router.post('/login/password/', responses={status.HTTP_401_UNAUTHORIZED: {'description': 'Could not validate credentials', 'model': DetailOnlyResponse}})
async def login(
    user: typing.Annotated[models.User, Depends(authenticate_user_with_username_and_password)],
    response: Response,
    stay_signed_in: bool = Form(c.authentication['stay_signed_in_default'])
) -> LoginResponse:

    with Session(c.db_engine) as session:

        user_access_token = await models.UserAccessToken.api_post(
            session=session, c=c, authorized_user_id=user._id, admin=False, create_model=models.UserAccessTokenCreateAdmin(
                user_id=user.id, lifespan=c.authentication['default_expiry_timedelta']
            )
        )

        set_access_token_cookie(jwt_encode(
            user_access_token.export_to_jwt()), response, stay_signed_in)

        return LoginResponse(
            auth=GetAuthBaseReturn(
                user=models.UserPrivate.model_validate(user),
                scope_ids=set(
                    c.user_role_id_scope_ids[user.user_role_id]),
                expiry=user_access_token.expiry,
                auth_credential=AuthCredentialIdAndType(
                    id=user_access_token.id, type='access_token')
            )
        )


class SignupResponse(GetAuthReturn):
    pass


@ auth_router.post('/signup/', responses={status.HTTP_409_CONFLICT: {"description": models.User.already_exists_message(), 'model': DetailOnlyResponse}})
async def sign_up(
    response: Response,
    email: models.UserTypes.email = Form(...),
    password: models.UserTypes.password = Form(...),
    stay_signed_in: bool = Form(c.authentication['stay_signed_in_default'])
) -> SignupResponse:

    user_create_admin = models.UserCreateAdmin(
        email=email, password=password, user_role_id=c.user_role_name_mapping['user'])

    with Session(c.db_engine) as session:
        user = await models.User.api_post(session=session, c=c, authorized_user_id=None,
                                          admin=False, create_model=user_create_admin)

        user_access_token = await models.UserAccessToken.api_post(
            session=session, c=c, authorized_user_id=user._id, admin=False, create_model=models.UserAccessTokenCreateAdmin(
                user_id=user._id, type='access_token', lifespan=c.authentication['default_expiry_timedelta']
            ))

        set_access_token_cookie(jwt_encode(
            user_access_token.export_to_jwt()), response, stay_signed_in)

        return SignupResponse(auth=GetAuthBaseReturn(
            user=models.UserPrivate.model_validate(user),
            scope_ids=set(
                c.user_role_id_scope_ids[user.user_role_id]),
            expiry=user_access_token.expiry,
            auth_credential=AuthCredentialIdAndType(
                id=user_access_token.id, type='access_token')
        ))


class LoginWithEmailMagicLinkRequest(BaseModel):
    email: models.UserTypes.email
    stay_signed_in: bool = False


async def send_magic_link_to_email(model: LoginWithEmailMagicLinkRequest):

    with Session(c.db_engine) as session:
        user = session.exec(select(models.User).where(
            models.User.email == model.email)).one_or_none()

        if user:
            user_access_token = await models.UserAccessToken.api_post(
                session=session, c=c, authorized_user_id=None, admin=False,
                create_model=models.UserAccessTokenCreateAdmin(user_id=user.id, lifespan=c.authentication['magic_link_expiry_timedelta']
                                                               ))

            link_data = {
                'access_token': jwt_encode(user_access_token.export_to_jwt()),
                'stay_signed_in': model.stay_signed_in
            }

            print('beep boop beep... sending email')
            print('http://localhost:3000' +
                  c.magic_link_frontend_url +
                  '?' + urlencode(link_data)
                  )


@ auth_router.post('/login/email-magic-link/')
async def login_with_email_magic_link(model: LoginWithEmailMagicLinkRequest, background_tasks: BackgroundTasks) -> DetailOnlyResponse:
    background_tasks.add_task(send_magic_link_to_email, model)
    return DetailOnlyResponse(detail='If an account with this email exists, a login link has been sent.')


class VerifyMagicLinkRequest(BaseModel):
    stay_signed_in: bool = False


class VerifyMagicLinkResponse(GetAuthReturn):
    pass


@ auth_router.post('/verify-magic-link/', responses={status.HTTP_401_UNAUTHORIZED: {'description': 'Invalid token', 'model': DetailOnlyResponse}})
async def verify_magic_link(model: VerifyMagicLinkRequest, authorization: typing.Annotated[GetAuthorizationReturn, Depends(get_authorization(permitted_auth_credential_types={'access_token'},
                                                                                                                                             override_lifetime=c.authentication['magic_link_expiry_timedelta']))], response: Response) -> VerifyMagicLinkResponse:
    with Session(c.db_engine) as session:

        user_access_token = await models.UserAccessToken.api_post(
            session=session, c=c, authorized_user_id=None, admin=False, create_model=models.UserAccessTokenCreateAdmin(
                user_id=authorization.user.id, lifespan=c.authentication['default_expiry_timedelta']
            )
        )
        set_access_token_cookie(jwt_encode(
            user_access_token.export_to_jwt()), response, model.stay_signed_in
        )

        # one time link, delete the auth_credential
        session.delete(authorization.auth_credential)
        session.commit()

        return VerifyMagicLinkResponse(
            auth=GetAuthBaseReturn(
                user=models.UserPrivate.model_validate(authorization.user),
                scope_ids=set(
                    c.user_role_id_scope_ids[authorization.user.user_role_id]),
                expiry=user_access_token.expiry,
                auth_credential=AuthCredentialIdAndType(
                    id=user_access_token.id, type='access_token')
            )
        )


class GoogleAuthResponse(LoginResponse):
    pass


class GoogleAuthRequest(BaseModel):
    access_token: str


@ auth_router.post("/login/google/", responses={status.HTTP_400_BAD_REQUEST: {"description": 'Invalid token'}})
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

        user = session.exec(select(models.User).where(
            models.User.email == email)).one_or_none()
        if not user:
            user = await models.User.api_post(session=session, c=c, authorized_user_id=None, admin=False, create_model=models.UserCreateAdmin(email=email))

        user_access_token = await models.UserAccessToken.api_post(
            session=session, c=c, authorized_user_id=None, admin=False, create_model=models.UserAccessTokenCreateAdmin(
                user_id=user.id, lifespan=c.authentication['default_expiry_timedelta']
            ))

        set_access_token_cookie(jwt_encode(
            user_access_token.export_to_jwt()), response)

        return VerifyMagicLinkResponse(
            auth=GetAuthBaseReturn(
                user=models.UserPrivate.model_validate(user),
                scope_ids=set(
                    c.user_role_id_scope_ids[user.user_role_id]),
                expiry=user_access_token.expiry,
                auth_credential=AuthCredentialIdAndType(
                    id=user_access_token.id, type='access_token')
            )
        )


@ auth_router.post('/logout/')
async def logout(response: Response, authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(raise_exceptions=False, permitted_auth_credential_types={'access_token'}))]) -> DetailOnlyResponse:

    if authorization.auth_credential:
        if authorization.auth_credential.type == 'access_token':
            with Session(c.db_engine) as session:
                await models.UserAccessToken.api_delete(session=session, c=c, authorized_user_id=authorization.user.id, id=authorization.auth_credential.id, admin=False)

    delete_access_token_cookie(response)
    return DetailOnlyResponse(detail='Logged out')

app.include_router(auth_router)


def get_pagination(max_limit: int = 100, default_limit: int = 10):
    def dependency(limit: int = Query(default_limit, ge=1, le=max_limit, description='Quantity of results'), offset: int = Query(0, ge=0, description='Index of the first result')):
        return models.Pagination(limit=limit, offset=offset)
    return dependency


# Users
user_router = APIRouter(prefix='/users', tags=[models.User._ROUTER_TAG])
user_admin_router = APIRouter(
    prefix='/admin/users', tags=[models.User._ROUTER_TAG, 'Admin'])


@user_router.get('/me/', responses=models.User.get_responses())
async def get_user_me(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization())]
) -> models.UserPrivate:
    return models.UserPrivate.model_validate(authorization.user)


@user_router.get('/{user_id}/', responses=models.User.get_responses())
async def get_user_by_id(
    user_id: models.UserTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(raise_exceptions=False))]
) -> models.UserPublic:
    with Session(c.db_engine) as session:
        return models.UserPublic.model_validate(await models.User.api_get(session=session, c=c, authorized_user_id=authorization._user_id, id=user_id, admin=False))


@user_admin_router.get('/{user_id}/', responses=models.User.get_responses())
async def get_user_by_id_admin(
    user_id: models.UserTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))]
) -> models.User:
    with Session(c.db_engine) as session:
        return await models.User.api_get(session=session, c=c, authorized_user_id=authorization._user_id, id=user_id, admin=True)


@user_admin_router.post('/', responses=models.User.post_responses())
async def post_user_admin(
    user_create_admin: models.UserCreateAdmin,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))]
) -> models.User:
    with Session(c.db_engine) as session:
        return await models.User.api_post(session=session, c=c, authorized_user_id=authorization._user_id, admin=True, create_model=user_create_admin)


@user_router.patch('/me/', responses=models.User.patch_responses())
async def patch_self(
    user_update: models.UserUpdate,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization())]
) -> models.UserPrivate:
    with Session(c.db_engine) as session:
        return models.UserPrivate.model_validate(await models.User.api_patch(session=session, c=c, authorized_user_id=authorization._user_id, id=authorization._user_id, admin=False, update_model=models.UserUpdateAdmin(**user_update.model_dump(exclude_unset=True))))


@user_admin_router.patch('/{user_id}/', responses=models.User.patch_responses())
async def patch_user_admin(
    user_id: models.UserTypes.id,
    user_update_admin: models.UserUpdateAdmin,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))]
) -> models.User:
    with Session(c.db_engine) as session:
        return await models.User.api_patch(session=session, c=c, authorized_user_id=authorization._user_id, id=user_id, admin=True, update_model=user_update_admin)


@user_router.delete('/me/', responses=models.User.delete_responses(), status_code=status.HTTP_204_NO_CONTENT)
async def delete_self(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization())]
):
    with Session(c.db_engine) as session:
        return await models.User.api_delete(session=session, c=c, authorized_user_id=authorization._user_id, id=authorization._user_id, admin=False)


@user_admin_router.delete('/{user_id}/', responses=models.User.delete_responses(), status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_admin(
    user_id: models.UserTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))]
):
    with Session(c.db_engine) as session:
        return await models.User.api_delete(session=session, c=c, authorized_user_id=authorization._user_id, id=user_id, admin=True)


@user_router.get('/', responses=models.User.post_responses())
async def get_users(
    pagination: typing.Annotated[models.Pagination, Depends(get_pagination())]
) -> list[models.UserPublic]:

    with Session(c.db_engine) as session:
        query = select(models.User).where(models.User.username != None)
        query = models.build_pagination(query, pagination)
        users = session.exec(query).all()
        return [models.UserPublic.model_validate(user) for user in users]


@user_admin_router.get('/')
async def get_users_admin(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))],
    pagination: typing.Annotated[models.Pagination, Depends(get_pagination())]
) -> list[models.User]:

    with Session(c.db_engine) as session:
        query = select(models.User)
        query = models.build_pagination(query, pagination)
        users = session.exec(query).all()
        return users


@ user_router.get('/available/username/{username}/',
                  responses={status.HTTP_409_CONFLICT: {
                      "description": 'Username already exists', 'model': DetailOnlyResponse}})
async def get_user_username_available(username: models.UserTypes.username):
    with Session(c.db_engine) as session:
        return await models.User.api_get_is_username_available(session, username)


@ user_router.get('/available/email/{email}/',
                  responses={status.HTTP_409_CONFLICT: {
                      "description": 'Email already exists', 'model': DetailOnlyResponse}})
async def get_user_email_available(email: models.UserTypes.email):
    with Session(c.db_engine) as session:
        await models.User.api_get_is_email_available(session, email)

app.include_router(user_router)
app.include_router(user_admin_router)


# User Access Tokens

user_access_token_router = APIRouter(
    prefix='/user-access-tokens', tags=[models.UserAccessToken._ROUTER_TAG])
user_access_token_admin_router = APIRouter(
    prefix='/admin/user-access-tokens', tags=[models.UserAccessToken._ROUTER_TAG, 'Admin'])


@user_access_token_router.get('/{user_access_token_id}/', responses=models.UserAccessToken.get_responses())
async def get_user_access_token_by_id(
    user_access_token_id: models.UserAccessTokenTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization())]
) -> models.UserAccessToken:
    with Session(c.db_engine) as session:
        return await models.UserAccessToken.api_get(session=session, c=c, authorized_user_id=authorization._user_id, id=user_access_token_id, admin=False)


@user_access_token_admin_router.get('/{user_access_token_id}/', responses=models.UserAccessToken.get_responses())
async def get_user_access_token_by_id_admin(
    user_access_token_id: models.UserAccessTokenTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))]
) -> models.UserAccessToken:
    with Session(c.db_engine) as session:
        return await models.UserAccessToken.api_get(session=session, c=c, authorized_user_id=authorization._user_id, id=user_access_token_id, admin=True)


@user_access_token_admin_router.post('/', responses=models.UserAccessToken.post_responses())
async def post_user_access_token_admin(
    user_access_token_create_admin: models.UserAccessTokenCreateAdmin,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))]
) -> models.UserAccessToken:
    with Session(c.db_engine) as session:
        return await models.UserAccessToken.api_post(session=session, c=c, authorized_user_id=authorization._user_id, admin=True, create_model=user_access_token_create_admin)


@user_access_token_router.delete('/{user_access_token_id}/', responses=models.UserAccessToken.delete_responses(), status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_access_token(
    user_access_token_id: models.UserAccessTokenTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization())]
):
    with Session(c.db_engine) as session:
        return await models.UserAccessToken.api_delete(session=session, c=c, authorized_user_id=authorization._user_id, id=user_access_token_id, admin=False)


@user_access_token_admin_router.delete('/{user_access_token_id}/', responses=models.UserAccessToken.delete_responses(), status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_access_token_admin(
    user_access_token_id: models.UserAccessTokenTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))]
):
    with Session(c.db_engine) as session:
        return await models.UserAccessToken.api_delete(session=session, c=c, authorized_user_id=authorization._user_id, id=user_access_token_id, admin=True)


WrongUserPermissionUserAccessToken = HTTPException(
    status.HTTP_403_FORBIDDEN, detail='User does not have permission to view another user\'s access tokens')


@ user_access_token_router.get('/', tags=[models.User._ROUTER_TAG], responses={status.HTTP_404_NOT_FOUND: {"description": models.User.not_found_message(), 'model': NotFoundResponse}, WrongUserPermissionUserAccessToken.status_code: {'description': WrongUserPermissionUserAccessToken.detail, 'model': DetailOnlyResponse}})
async def get_user_access_tokens(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization())],
    pagination: typing.Annotated[models.Pagination, Depends(
        get_pagination())]

) -> list[models.UserAccessToken]:
    with Session(c.db_engine) as session:
        query = select(models.UserAccessToken).where(
            models.UserAccessToken.user_id == authorization._user_id)
        query = models.build_pagination(query, pagination)
        user_access_tokens = session.exec(query).all()
        return user_access_tokens


@user_access_token_admin_router.get('/users/{user_id}/', tags=[models.User._ROUTER_TAG], responses={status.HTTP_404_NOT_FOUND: {"description": models.User.not_found_message(), 'model': NotFoundResponse}})
async def get_user_access_tokens_admin(
    user_id: models.UserTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))],
    pagination: typing.Annotated[models.Pagination, Depends(
        get_pagination())]
) -> list[models.UserAccessToken]:
    with Session(c.db_engine) as session:

        query = select(models.UserAccessToken).where(
            models.UserAccessToken.user_id == user_id)
        query = models.build_pagination(query, pagination)
        user_access_tokens = session.exec(query).all()
        return user_access_tokens


app.include_router(user_access_token_router)
app.include_router(user_access_token_admin_router)


# API Keys


api_key_router = APIRouter(
    prefix='/api-keys', tags=[models.ApiKey._ROUTER_TAG])
api_key_admin_router = APIRouter(
    prefix='/admin/api-keys', tags=[models.ApiKey._ROUTER_TAG, 'Admin'])


@ api_key_router.get('/{api_key_id}/', responses=models.ApiKey.get_responses())
async def get_api_key_by_id(
    api_key_id: models.ApiKeyTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization())]
) -> models.ApiKeyPrivate:
    with Session(c.db_engine) as session:
        return models.ApiKeyPrivate.model_validate(await models.ApiKey.api_get(session=session, c=c, authorized_user_id=authorization.user.id, id=api_key_id, admin=False))


@api_key_admin_router.get('/{api_key_id}/', responses=models.ApiKey.get_responses())
async def get_api_key_by_id_admin(
    api_key_id: models.ApiKeyTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))]
) -> models.ApiKey:
    with Session(c.db_engine) as session:
        return await models.ApiKey.api_get(session=session, c=c, authorized_user_id=authorization.user.id, id=api_key_id, admin=True)


@api_key_router.post('/', responses=models.ApiKey.post_responses())
async def post_api_key_to_user(
    api_key_create: models.ApiKeyCreate,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization())]
) -> models.ApiKeyPrivate:

    with Session(c.db_engine) as session:
        return models.ApiKeyPrivate.model_validate(await models.ApiKey.api_post(session=session, c=c, authorized_user_id=authorization._user_id, admin=False, create_model=models.ApiKeyCreateAdmin(
            **api_key_create.model_dump(exclude_unset=True), user_id=authorization._user_id)))


@api_key_admin_router.post('/', responses=models.ApiKey.post_responses())
async def post_api_key_to_user_admin(
    api_key_create_admin: models.ApiKeyCreateAdmin,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))]
) -> models.ApiKey:
    with Session(c.db_engine) as session:
        return await models.ApiKey.api_post(session=session, c=c, authorized_user_id=authorization.user.id, admin=True, create_model=models.ApiKeyCreateAdmin(**api_key_create_admin.model_dump(exclude_unset=True)))


@api_key_router.patch('/{api_key_id}/', responses=models.ApiKey.patch_responses())
async def patch_api_key(
    api_key_id: models.ApiKeyTypes.id,
    api_key_update: models.ApiKeyUpdate,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization())]
) -> models.ApiKeyPrivate:
    with Session(c.db_engine) as session:
        return models.ApiKeyPrivate.model_validate(await models.ApiKey.api_patch(session=session, c=c, authorized_user_id=authorization.user.id, id=api_key_id, admin=False, update_model=models.ApiKeyUpdateAdmin(**api_key_update.model_dump(exclude_unset=True))))


@api_key_admin_router.patch('/{api_key_id}/', responses=models.ApiKey.patch_responses())
async def patch_api_key_admin(
    api_key_id: models.ApiKeyTypes.id,
    api_key_update_admin: models.ApiKeyUpdateAdmin,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))]
) -> models.ApiKey:
    with Session(c.db_engine) as session:
        return await models.ApiKey.api_patch(session=session, c=c, authorized_user_id=authorization.user.id, id=api_key_id, admin=True, update_model=models.ApiKeyUpdateAdmin(**api_key_update_admin.model_dump(exclude_unset=True)))


@api_key_router.delete('/{api_key_id}/', responses=models.ApiKey.delete_responses(), status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    api_key_id: models.ApiKeyTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization())]
):
    with Session(c.db_engine) as session:
        return await models.ApiKey.api_delete(session=session, c=c, authorized_user_id=authorization.user.id, id=api_key_id, admin=False)


@api_key_admin_router.delete('/{api_key_id}/', responses=models.ApiKey.delete_responses(), status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key_admin(
    api_key_id: models.ApiKeyTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))]
):
    with Session(c.db_engine) as session:
        return await models.ApiKey.api_delete(session=session, c=c, authorized_user_id=authorization.user.id, id=api_key_id, admin=True)


class ApiKeyJWTResponse(BaseModel):
    jwt: str


@ api_key_router.get('/{api_key_id}/generate-jwt/', responses={status.HTTP_404_NOT_FOUND: {"description": models.ApiKey.not_found_message(), 'model': NotFoundResponse}})
async def get_api_key_jwt(
    api_key_id: models.ApiKeyTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization())]
) -> ApiKeyJWTResponse:
    with Session(c.db_engine) as session:
        api_key = await models.ApiKey.api_get(session=session, c=c, authorized_user_id=authorization.user.id, id=api_key_id, admin=False)
        return ApiKeyJWTResponse(
            jwt=jwt_encode(api_key.export_to_jwt())
        )

UserNotPermittedToViewAnotherUserApiKeys = HTTPException(
    status.HTTP_403_FORBIDDEN, detail='User does not have permission to view another user\'s API keys')


@api_key_router.get('/')
async def get_user_api_keys(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization())],
    pagination: typing.Annotated[models.Pagination, Depends(get_pagination())],
    order_bys: typing.Annotated[list[models.OrderBy[models.ApiKeyTypes.order_by]], Depends(models.ApiKey.get_order_by_depends())],
) -> list[models.ApiKeyPrivate]:
    with Session(c.db_engine) as session:

        query = select(models.ApiKey).where(
            models.ApiKey.user_id == authorization._user_id)
        query = models.build_pagination(query, pagination)
        query = models.ApiKey._build_order_by(query, order_bys)

        print(query)

        user_api_keys = session.exec(query).all()
        return [models.ApiKeyPrivate.model_validate(api_key) for api_key in user_api_keys]


@api_key_admin_router.get('/users/{user_id}/', tags=[models.User._ROUTER_TAG])
async def get_user_api_keys_admin(
    user_id: models.UserTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))],
    pagination: typing.Annotated[models.Pagination, Depends(get_pagination())],
    order_bys: typing.Annotated[list[models.OrderBy[models.ApiKeyTypes.order_by]], Depends(models.ApiKey.get_order_by_depends())],
) -> list[models.ApiKey]:
    with Session(c.db_engine) as session:

        query = select(models.ApiKey).where(
            models.ApiKey.user_id == user_id)
        query = models.build_pagination(query, pagination)
        query = models.ApiKey._build_order_by(query, order_bys)

        user_api_keys = session.exec(query).all()
        return user_api_keys


@api_key_router.get('/available/check/', responses={status.HTTP_409_CONFLICT: {"description": models.ApiKey.already_exists_message(), 'model': DetailOnlyResponse}})
async def get_api_key_available(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization())],
    api_key_available: models.ApiKeyAvailable = Depends(),
):
    with Session(c.db_engine) as session:
        await models.ApiKey.api_get_is_available(session, models.ApiKeyAvailableAdmin(
            **api_key_available.model_dump(exclude_unset=True), user_id=authorization.user.id
        ))


@api_key_admin_router.get('/available/check/', responses={status.HTTP_409_CONFLICT: {"description": models.ApiKey.already_exists_message(), 'model': DetailOnlyResponse}})
async def get_api_key_available_admin(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))],
    api_key_available_admin: models.ApiKeyAvailableAdmin = Depends(),
):
    with Session(c.db_engine) as session:
        await models.ApiKey.api_get_is_available(session, api_key_available_admin)


app.include_router(api_key_router)
app.include_router(api_key_admin_router)


# API Key Scope


api_key_scope_router = APIRouter(
    prefix='/api-key-scopes', tags=[models.ApiKeyScope._ROUTER_TAG])
api_key_scope_admin_router = APIRouter(
    prefix='/admin/api-key-scopes', tags=[models.ApiKeyScope._ROUTER_TAG, 'Admin'])


@ api_key_scope_router.post('/api-keys/{api_key_id}/scopes/{scope_id}/',
                            responses={status.HTTP_404_NOT_FOUND: {
                                "description": models.ApiKey.not_found_message(), 'model': NotFoundResponse}},
                            )
async def add_scope_to_api_key(
    api_key_id: models.ApiKeyTypes.id,
    scope_id: client.ScopeTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization())]
):
    with Session(c.db_engine) as session:
        return await models.ApiKeyScope.api_post(session=session, c=c, authorized_user_id=authorization.user.id, create_model=models.ApiKeyScopeCreateAdmin(api_key_id=api_key_id, scope_id=scope_id), admin=False)


@api_key_scope_admin_router.post('/api-keys/{api_key_id}/scopes/{scope_id}/',
                                 responses={status.HTTP_404_NOT_FOUND: {
                                     "description": models.ApiKey.not_found_message(), 'model': NotFoundResponse}},
                                 )
async def add_scope_to_api_key_admin(
    api_key_id: models.ApiKeyTypes.id,
    scope_id: client.ScopeTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))]
):
    with Session(c.db_engine) as session:
        return await models.ApiKeyScope.api_post(session=session, c=c, authorized_user_id=authorization.user.id, create_model=models.ApiKeyScopeCreateAdmin(api_key_id=api_key_id, scope_id=scope_id), admin=True)


@ api_key_scope_router.delete('/api-keys/{api_key_id}/scopes/{scope_id}/',
                              responses={status.HTTP_404_NOT_FOUND: {
                                  "description": models.ApiKey.not_found_message(), 'model': NotFoundResponse}},
                              status_code=status.HTTP_204_NO_CONTENT,
                              )
async def remove_scope_from_api_key(
    api_key_id: models.ApiKeyTypes.id,
    scope_id: client.ScopeTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization())]
):
    with Session(c.db_engine) as session:
        return await models.ApiKeyScope.api_delete(session=session, c=c, authorized_user_id=authorization.user.id, id=models.ApiKeyScopeIdBase(api_key_id=api_key_id, scope_id=scope_id)._id, admin=False)


@api_key_scope_admin_router.delete('/api-keys/{api_key_id}/scopes/{scope_id}/',
                                   responses={status.HTTP_404_NOT_FOUND: {
                                       "description": models.ApiKey.not_found_message(), 'model': NotFoundResponse}},
                                   status_code=status.HTTP_204_NO_CONTENT,
                                   )
async def remove_scope_from_api_key_admin(
    api_key_id: models.ApiKeyTypes.id,
    scope_id: client.ScopeTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))]
):
    with Session(c.db_engine) as session:
        return await models.ApiKeyScope.api_delete(session=session, c=c, authorized_user_id=authorization.user.id, id=models.ApiKeyScopeIdBase(api_key_id=api_key_id, scope_id=scope_id)._id, admin=True)

app.include_router(api_key_scope_router)
app.include_router(api_key_scope_admin_router)


# galleries


gallery_router = APIRouter(
    prefix='/galleries', tags=[models.Gallery._ROUTER_TAG])
gallery_admin_router = APIRouter(prefix='/admin/galleries', tags=[
    models.Gallery._ROUTER_TAG, 'Admin'])


@gallery_router.get('/{gallery_id}/', responses=models.Gallery.get_responses())
async def get_gallery_by_id(
    gallery_id: models.GalleryTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(raise_exceptions=False))]
) -> models.GalleryPublic:
    with Session(c.db_engine) as session:
        return models.GalleryPublic.model_validate(await models.Gallery.api_get(session=session, c=c, authorized_user_id=authorization._user_id, id=gallery_id, admin=False))


@gallery_admin_router.get('/{gallery_id}/', responses=models.Gallery.get_responses())
async def get_gallery_by_id_admin(
    gallery_id: models.GalleryTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))]
) -> models.Gallery:
    with Session(c.db_engine) as session:
        return await models.Gallery.api_get(session=session, c=c, authorized_user_id=authorization._user_id, id=gallery_id, admin=True)


@gallery_router.post('/', responses=models.Gallery.post_responses())
async def post_gallery(
    gallery_create: models.GalleryCreate,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization())]
) -> models.GalleryPrivate:
    with Session(c.db_engine) as session:
        return models.GalleryPrivate.model_validate(await models.Gallery.api_post(session=session, c=c, authorized_user_id=authorization._user_id, admin=False, create_model=models.GalleryCreateAdmin(**gallery_create.model_dump(exclude_unset=True))))


@gallery_admin_router.post('/', responses=models.Gallery.post_responses())
async def post_gallery_admin(
    gallery_create_admin: models.GalleryCreateAdmin,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))]
) -> models.Gallery:
    with Session(c.db_engine) as session:
        return await models.Gallery.api_post(session=session, c=c, authorized_user_id=authorization._user_id, admin=True, create_model=models.GalleryCreateAdmin(**gallery_create_admin.model_dump(exclude_unset=True)))


@gallery_router.patch('/{gallery_id}/', responses=models.Gallery.patch_responses())
async def patch_gallery(
    gallery_id: models.GalleryTypes.id,
    gallery_update: models.GalleryUpdate,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization())]
) -> models.GalleryPrivate:
    with Session(c.db_engine) as session:
        return models.GalleryPrivate.model_validate(await models.Gallery.api_patch(session=session, c=c, authorized_user_id=authorization._user_id, id=gallery_id, admin=False, update_model=models.GalleryUpdateAdmin(**gallery_update.model_dump(exclude_unset=True))))


@gallery_admin_router.patch('/{gallery_id}/', responses=models.Gallery.patch_responses())
async def patch_gallery_admin(
    gallery_id: models.GalleryTypes.id,
    gallery_update_admin: models.GalleryUpdateAdmin,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))]
) -> models.Gallery:
    with Session(c.db_engine) as session:
        return await models.Gallery.api_patch(session=session, c=c, authorized_user_id=authorization._user_id, id=gallery_id, admin=True, update_model=models.GalleryUpdateAdmin(**gallery_update_admin.model_dump(exclude_unset=True)))


@gallery_router.delete('/{gallery_id}/', responses=models.Gallery.delete_responses(), status_code=status.HTTP_204_NO_CONTENT)
async def delete_gallery(
    gallery_id: models.GalleryTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization())]
):
    with Session(c.db_engine) as session:
        return await models.Gallery.api_delete(session=session, c=c, authorized_user_id=authorization._user_id, id=gallery_id, admin=False)


@gallery_admin_router.delete('/{gallery_id}/', responses=models.Gallery.delete_responses(), status_code=status.HTTP_204_NO_CONTENT)
async def delete_gallery_admin(
    gallery_id: models.GalleryTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))]
):
    with Session(c.db_engine) as session:
        return await models.Gallery.api_delete(session=session, c=c, authorized_user_id=authorization._user_id, id=gallery_id, admin=True)


@gallery_router.get('/available/check/')
async def get_gallery_available(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization())],
    gallery_available: models.GalleryAvailable = Depends(),
):
    with Session(c.db_engine) as session:
        await models.Gallery.api_get_is_available(session, models.GalleryAvailableAdmin(
            **gallery_available.model_dump(exclude_unset=True), user_id=authorization.user.id
        ))


@gallery_admin_router.get('/available/check/')
async def get_gallery_available_admin(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))],
    gallery_available_admin: models.GalleryAvailableAdmin = Depends(),
):
    with Session(c.db_engine) as session:
        await models.Gallery.api_get_is_available(session, gallery_available_admin)


@gallery_router.get('/')
async def get_galleries(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization())],
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> list[models.GalleryPrivate]:

    with Session(c.db_engine) as session:
        galleries = session.exec(select(models.Gallery).where(
            models.Gallery.user_id == authorization._user_id).offset(offset).limit(limit)).all()
        return [models.GalleryPrivate.model_validate(gallery) for gallery in galleries]


# need to decide how to deal with gallery permissions and how to return

# @gallery_router.get('/users/{user_id}/', tags=[models.User._ROUTER_TAG])
# async def get_galleries_by_user(
#     user_id: models.UserTypes.id,
#     authorization: typing.Annotated[GetAuthorizationReturn, Depends(
#         get_authorization(raise_exceptions=False))],
#     pagination: PaginationParams = Depends(get_pagination_params),
# ) -> list[models.GalleryPublic]:

#     with Session(c.db_engine) as session:
#         galleries = session.exec(select(models.Gallery).where(
#             models.Gallery.user_id == user_id).offset(pagination.offset).limit(pagination.limit)).all()
#         return [models.GalleryPublic.model_validate(gallery) for gallery in galleries]


@gallery_admin_router.get('/users/{user_id}', tags=[models.User._ROUTER_TAG])
async def get_galleries_by_user_admin(
    user_id: models.UserTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(required_scopes={'admin'}))],
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> list[models.Gallery]:

    with Session(c.db_engine) as session:
        galleries = session.exec(select(models.Gallery).where(
            models.Gallery.user_id == user_id).offset(offset).limit(limit)).all()
        return galleries


class UploadFileToGalleryResponse(BaseModel):
    message: str


@ gallery_router.post("/{gallery_id}/upload/", status_code=status.HTTP_201_CREATED)
async def upload_file_to_gallery(
    gallery_id: models.GalleryTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization())],
    file: UploadFile = File(...)
) -> UploadFileToGalleryResponse:

    # with Session(c.db_engine) as session:
    #     gallery = await models.Gallery.get(session, gallery_id)
    #     if not gallery:
    #         raise HTTPException(status.HTTP_404_NOT_FOUND,
    #                             detail=models.Gallery.not_found_message())

    #     gallery_permission = await models.GalleryPermission.get(
    #         session, (gallery_id, authorization.user.id))

    #     if not gallery_permission:
    #         raise HTTPException(status.HTTP_404_NOT_FOUND,
    #                             detail=models.Gallery.not_found_message())
    #     if gallery_permission.permission_level < c.permission_level_name_mapping['editor']:
    #         raise HTTPException(status.HTTP_403_FORBIDDEN,
    #                             detail='User does not have permission to add files to this gallery')

    #     print(file.__dict__)
    #     file_path = gallery.get_dir(c.galleries_dir) / file.filename
    #     with open(file_path, "wb") as buffer:
    #         shutil.copyfileobj(file.file, buffer)

    return UploadFileToGalleryResponse(message="Files uploaded successfully")


@ gallery_router.post('/{gallery_id}/sync/')
async def sync_gallery(
    gallery_id: models.GalleryTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization())]
) -> DetailOnlyResponse:

    with Session(c.db_engine) as session:
        gallery = await models.Gallery.api_get(session=session, c=c, authorized_user_id=authorization.user.id, id=gallery_id, admin=False)
        dir = await gallery.get_dir(session, c.galleries_dir)
        await gallery.sync_with_local(session, c, dir)
        return DetailOnlyResponse(detail='Synced gallery')

app.include_router(gallery_router)
app.include_router(gallery_admin_router)


# Pages


pages_router = APIRouter(prefix='/pages', tags=['Page'])


class GetProfilePageResponse(GetAuthReturn):
    user: models.UserPrivate | None = None


@ pages_router.get('/profile/', tags=[models.User._ROUTER_TAG])
async def get_pages_profile(authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization())]) -> GetProfilePageResponse:

    return GetProfilePageResponse(
        **get_auth(authorization).model_dump(),
        user=models.UserPrivate.model_validate(authorization.user)
    )


class GetHomePageResponse(GetAuthReturn):
    pass


@ pages_router.get('/home/')
async def get_home_page(authorization: typing.Annotated[GetAuthorizationReturn, Depends(get_authorization(raise_exceptions=False))]) -> GetHomePageResponse:
    return GetHomePageResponse(
        **get_auth(authorization).model_dump()
    )


class GetSettingsPageResponse(GetAuthReturn):
    pass


@ pages_router.get('/settings/')
async def get_settings_page(authorization: typing.Annotated[GetAuthorizationReturn, Depends(get_authorization(raise_exceptions=False))]) -> GetSettingsPageResponse:
    return GetSettingsPageResponse(
        **get_auth(authorization).model_dump()
    )


class GetSettingsApiKeysPageResponse(GetAuthReturn):
    api_keys: models.PluralApiKeysDict
    api_key_scope_ids: dict[models.ApiKeyTypes.id, list[client.ScopeTypes.id]]


class GetStylesPageResponse(GetAuthReturn):
    pass


@pages_router.get('/styles/')
async def get_styles_page(authorization: typing.Annotated[GetAuthorizationReturn, Depends(get_authorization(raise_exceptions=False))]) -> GetStylesPageResponse:
    return GetStylesPageResponse(
        **get_auth(authorization).model_dump()
    )


class GetGalleryPageResponse(GetAuthReturn):
    gallery: models.GalleryPublic
    parents: list[models.GalleryPublic]
    children: list[models.GalleryPublic]


@ pages_router.get('/galleries/{gallery_id}/', responses={status.HTTP_404_NOT_FOUND: {"description": models.Gallery.not_found_message(), 'model': NotFoundResponse}}, tags=[models.Gallery._ROUTER_TAG])
async def get_gallery_page(
    gallery_id: models.GalleryTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(raise_exceptions=False))],
    root: bool = Query(False),
) -> GetGalleryPageResponse:

    if root:
        with Session(c.db_engine) as session:
            if not authorization.isAuthorized:
                raise HTTPException(status.HTTP_404_NOT_FOUND,
                                    detail=models.Gallery.not_found_message())

            gallery = await models.Gallery.get_root_gallery(session, authorization.user.id)
            gallery_id = gallery._id

    with Session(c.db_engine) as session:
        gallery = await models.Gallery.api_get(
            session=session, c=c, authorized_user_id=None if not authorization.isAuthorized else authorization.user.id, id=gallery_id, admin=False)

        return GetGalleryPageResponse(
            **get_auth(authorization).model_dump(),
            gallery=models.GalleryPublic.model_validate(gallery),
            parents=[models.GalleryPublic.model_validate(
                parent) for parent in await gallery.get_parents(session)],
            children=[models.GalleryPublic.model_validate(
                child) for child in gallery.children]
        )


# add the non admin routers first

app.include_router(pages_router)


# add the admin routers last

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
