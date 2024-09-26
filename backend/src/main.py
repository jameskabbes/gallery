import uvicorn
from fastapi import FastAPI, HTTPException, Query, status, Response, Depends, Request, BackgroundTasks, Form
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2, OAuth2PasswordRequestForm, OAuth2PasswordBearer, APIKeyHeader
from fastapi.security.utils import get_authorization_scheme_param
from contextlib import asynccontextmanager
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


def make_auth_credential(
    user_id: models.UserTypes.id,
    auth_credential_type: models.AuthCredentialType,
    lifespan: typing.Annotated[datetime.timedelta | None,
                               'The timedelta from token creation in which the token is still valid'] = c.authentication['default_expiry_timedelta'],
    expiry_datetime: typing.Annotated[datetime.datetime | None,
                                      'The datetime at which the token will expire'] = None
) -> models.AuthCredential:

    with Session(c.db_engine) as session:
        if expiry_datetime == None and lifespan == None:
            raise ValueError(
                'Either expiry_timedelta or expiry_datetime must be provided')

        if expiry_datetime == None:
            expiry_datetime = datetime.datetime.now(
                datetime.UTC) + lifespan

        auth_credential = models.AuthCredentialCreate(
            user_id=user_id,
            type=auth_credential_type,
            expiry=expiry_datetime
        ).create()
        auth_credential.add_to_db(session)
        return auth_credential


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
    auth_credential: models.AuthCredential | None = None


def get_authorization(
    required_scopes: set[models.ScopeTypes.name] = set(),
    override_lifetime: datetime.timedelta | None = None,
    raise_exceptions: bool = True,
    remove_cookie_on_exception: bool = True,
) -> typing.Callable[[str], GetAuthorizationReturn]:

    def dependecy(auth_token: typing.Annotated[str | None, Depends(oauth2_scheme)], response: Response) -> GetAuthorizationReturn:
        def inner() -> GetAuthorizationReturn:
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

            auth_credential_dict = models.AuthCredential.import_from_jwt(
                payload)

            with Session(c.db_engine) as session:

                # find the auth_credential in the db
                auth_credential = models.AuthCredential.get_one_by_id(session,
                                                                      auth_credential_dict['id'])

                # not in the db, raise exception
                if not auth_credential:
                    return GetAuthorizationReturn(exception='authorization_expired')

                dt_now = datetime.datetime.now(datetime.UTC)

                dt_exp_jwt = datetime.datetime.fromtimestamp(
                    payload['exp'], datetime.UTC)
                dt_exp_db = auth_credential.expiry.replace(tzinfo=datetime.UTC)
                dt_exp = min(dt_exp_jwt, dt_exp_db)

                if dt_now > dt_exp:
                    models.AuthCredential.delete_one_by_id(
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
                        models.AuthCredential.delete_one_by_id(
                            session, auth_credential.id)
                        return GetAuthorizationReturn(exception='authorization_expired')

                user = auth_credential.user
                if user == None:
                    return GetAuthorizationReturn(exception='user_not_found')

                auth_credential_type: models.AuthCredentialType = auth_credential.type
                scopes: list[models.Scope] = []
                if auth_credential_type == 'access_token':
                    # access_token scopes are tied to the user
                    scopes = [
                        user_role_scope.scope for user_role_scope in user.user_role.user_role_scopes]

                elif auth_credential_type == 'api_key':
                    # api key scopes are tied to the api key
                    scopes = [
                        auth_credential_scope.scope for auth_credential_scope in auth_credential.auth_credential_scopes]

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

        inner_response = inner()
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
    scopes: set[models.ScopeTypes.id] | None = None
    expiry: datetime.datetime | None = None


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


async def authenticate_user_with_password(form_data: typing.Annotated[OAuth2PasswordRequestForm, Depends()]) -> models.User:
    with Session(c.db_engine) as session:
        user = models.User.authenticate(
            session, form_data.username, form_data.password)
        if not user:
            raise auth.credentials_exception()
        return user


def set_access_token_cookie(access_token: str, response: Response):

    response.set_cookie(
        key=c.root_config['cookie_keys']['access_token'],
        value=access_token,
        httponly=True,
        secure=True,
        samesite="Lax",
        expires=datetime.datetime.now(
            datetime.UTC) + datetime.timedelta(days=1)
    )


@ app.post('/token/')
async def post_token(user: typing.Annotated[models.User, Depends(authenticate_user_with_password)], response: Response):

    auth_credential = make_auth_credential(
        user.id, 'access_token')
    set_access_token_cookie(jwt_encode(
        auth_credential.export_to_jwt()), response)

    return


class LoginResponse(GetAuthReturn):
    pass


@ app.post('/auth/login/password/', responses={status.HTTP_401_UNAUTHORIZED: {'description': 'Could not validate credentials', 'model': DetailOnlyResponse}})
async def login(user: typing.Annotated[models.User, Depends(authenticate_user_with_password)], response: Response) -> LoginResponse:

    auth_credential = make_auth_credential(user.id, 'access_token')
    set_access_token_cookie(jwt_encode(
        auth_credential.export_to_jwt()), response)

    return LoginResponse(
        auth=GetAuthBaseReturn(
            user=models.UserPrivate.model_validate(user),
            # [user_scope.scope.id for user_scope in user.scopes],
            scopes=set(),
            expiry=auth_credential.expiry
        )
    )


class SignupResponse(GetAuthReturn):
    pass


@ app.post('/auth/signup/', responses={status.HTTP_409_CONFLICT: {"description": 'User already exists', 'model': DetailOnlyResponse}})
async def sign_up(
    response: Response,
    email: models.UserTypes.email = Form(...),
    password: models.UserTypes.password = Form(...),
) -> SignupResponse:

    user_create = models.UserCreate(email=email, password=password)
    user = await post_user(user_create)
    auth_credential = make_auth_credential(user.id, 'access_token')
    set_access_token_cookie(jwt_encode(
        auth_credential.export_to_jwt()), response)

    return SignupResponse(
        auth=GetAuthBaseReturn(
            user=models.UserPrivate.model_validate(user),
            # [user_scope.scope.id for user_scope in user.scopes],
            scopes=set(),
            expiry=auth_credential.expiry
        )
    )


class LoginWithEmailMagicLinkRequest(BaseModel):
    email: models.UserTypes.email


def send_magic_link_to_email(model: LoginWithEmailMagicLinkRequest):

    with Session(c.db_engine) as session:
        user = models.User.get_one_by_key_values(
            session, {'email': model.email})

        if user:
            auth_credential = make_auth_credential(
                user_id=user.id, auth_credential_type='access_token', lifespan=c.authentication['magic_link_expiry_timedelta']
            )

            print('beep boop beep... sending email')
            print('http://localhost:3000' +
                  c.root_config['magic_link_frontend_url'] + '?access_token=' + jwt_encode(auth_credential.export_to_jwt()))

    # still need to fill this function in!


@ app.post('/auth/login/email-magic-link/')
async def login_with_email_magic_link(model: LoginWithEmailMagicLinkRequest, background_tasks: BackgroundTasks) -> DetailOnlyResponse:
    background_tasks.add_task(send_magic_link_to_email, model)
    return DetailOnlyResponse(detail='If an account with this email exists, a login link has been sent.')


class VerifyMagicLinkRequest(GetAuthReturn):
    pass


@ app.post('/auth/verify-magic-link/', responses={status.HTTP_401_UNAUTHORIZED: {'description': 'Invalid token', 'model': DetailOnlyResponse}})
async def verify_magic_link(authorization: typing.Annotated[GetAuthorizationReturn, Depends(get_authorization(raise_exceptions=True, override_lifetime=c.authentication['magic_link_expiry_timedelta']))], response: Response) -> VerifyMagicLinkRequest:

    auth_credential = make_auth_credential(
        authorization.user.id, 'access_token')
    set_access_token_cookie(jwt_encode(
        auth_credential.export_to_jwt()), response)

    # one time link, delete the auth_credential
    authorization.auth_credential.delete_one_by_id(
        authorization.auth_credential.id)

    return VerifyMagicLinkRequest(
        auth=GetAuthBaseReturn(
            user=models.UserPrivate.model_validate(authorization.user),
            # [user_scope.scope.id for user_scope in user.scopes],
            scopes=set(),
            expiry=auth_credential.expiry
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
        user = models.User.get_one_by_key_values(session, {'email': email})
        if not user:
            user_create = models.UserCreate(
                email=email,
            )
            user = user_create.create()
            user.add_to_db(session)

        auth_credential = make_auth_credential(
            user.id, 'access_token')
        set_access_token_cookie(jwt_encode(
            auth_credential.export_to_jwt()), response)

        return VerifyMagicLinkRequest(
            auth=GetAuthBaseReturn(
                user=models.UserPrivate.model_validate(user),
                # [user_scope.scope.id for user_scope in user.scopes],
                scopes=set(),
                expiry=auth_credential.expiry
            )
        )


def delete_access_token_cookie(response: Response):
    response.delete_cookie(c.root_config['cookie_keys']['access_token'])


@ app.post('/auth/logout/')
async def logout(response: Response, authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(raise_exceptions=False))]) -> DetailOnlyResponse:

    if authorization.auth_credential:
        with Session(c.db_engine) as session:
            models.AuthCredential.delete_one_by_id(session,
                                                   authorization.auth_credential.id)

    delete_access_token_cookie(response)
    return DetailOnlyResponse(detail='Logged out')

# # USERS


@ app.get('/users/available/username/{username}/')
async def user_username_available(username: models.UserTypes.username) -> ItemAvailableResponse:
    with Session(c.db_engine) as session:
        return ItemAvailableResponse(available=models.User.is_username_available(session, username))


@ app.get('/users/available/email/{email}/')
async def user_email_available(email: models.UserTypes.email) -> ItemAvailableResponse:
    with Session(c.db_engine) as session:
        return ItemAvailableResponse(available=models.User.is_email_available(session, email))


@ app.get('/users/username/{username}/', responses={status.HTTP_404_NOT_FOUND: {"description": models.User.not_found_message(), 'model': NotFoundResponse}})
async def get_user_by_username(
    username: models.UserTypes.username,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(raise_exceptions=False))]) -> models.UserPublic:

    with Session(c.db_engine) as session:
        user = models.User.get_one_by_key_values(
            session, {'username': username})
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail=models.User.not_found_message())
        else:
            return models.UserPublic.model_validate(user)


@ app.get('/users/{user_id}/', responses={status.HTTP_404_NOT_FOUND: {"description": models.User.not_found_message(), 'model': NotFoundResponse}})
async def get_user_by_id(
    user_id: models.UserTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(raise_exceptions=False))]) -> models.UserPublic:

    with Session(c.db_engine) as session:
        user = models.User.get_one_by_id(
            session, user_id)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail=models.User.not_found_message())

        # only allow yourself to access your info
        elif not user.is_public and user.id != authorization.user.id:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail=models.User.not_found_message())
        else:
            return models.UserPublic.model_validate(user)


@ app.get('/users/{user_id}/admin/', responses={status.HTTP_404_NOT_FOUND: {"description": models.User.not_found_message(), 'model': NotFoundResponse}})
async def get_user_by_id_admin(
    user_id: models.UserTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(raise_exceptions=True, required_scopes={'admin'}))]) -> models.User:

    with Session(c.db_engine) as session:
        user = models.User.get_one_by_id(
            session, user_id)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail=models.User.not_found_message())
        else:
            return user


@ app.post('/users/', responses={status.HTTP_409_CONFLICT: {"description": 'User already exists', 'model': DetailOnlyResponse}})
async def post_user(user_create: models.UserCreate) -> models.UserPrivate:
    with Session(c.db_engine) as session:
        # see if the email is available
        resp = await user_email_available(user_create.email)
        if not resp.available:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail='User already exists')
        user = user_create.create()
        user.add_to_db(session)
        return models.UserPrivate.model_validate(user)


@ app.patch('/users/{user_id}/', responses={
    status.HTTP_401_UNAUTHORIZED: {'description': 'Invalid token', 'model': DetailOnlyResponse},
    status.HTTP_403_FORBIDDEN: {"description": 'User does not have permission to update this user', 'model': DetailOnlyResponse},
    status.HTTP_404_NOT_FOUND: {"description": models.User.not_found_message(), 'model': NotFoundResponse},
    status.HTTP_409_CONFLICT: {"description": 'Username or email already exists', 'model': DetailOnlyResponse},
})
async def patch_user(
    user_id: models.UserTypes.id,
    user_update: models.UserUpdate,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(raise_exceptions=True))]
) -> models.UserPrivate:

    with Session(c.db_engine) as session:
        user = models.User.get_one_by_id(session, user_id)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail=models.User.not_found_message())

        if user.id != authorization.user.id:
            raise HTTPException(status.HTTP_403_FORBIDDEN,
                                detail='User does not have permission to update this user')

        # if they changed their username, check if it's available
        if user_update.username != None:
            if user.username != user_update.username:
                response = await user_username_available(user_update.username)
                if response.available == False:
                    raise HTTPException(status.HTTP_409_CONFLICT,
                                        detail='Username already exists')
        # if they changed their email, check if it's available
        if user_update.email != None:
            if user.email != user_update.email:
                response = await user_email_available(user_update.email)
                if response.available == False:
                    raise HTTPException(status.HTTP_409_CONFLICT,
                                        detail='Email already exists')
        update_fields = {}
        if user_update.email != None:
            update_fields['email'] = user_update.email
        if user_update.username != None:
            update_fields['username'] = user_update.username
        if user_update.password != None:
            update_fields['hashed_password'] = utils.hash_password(
                user_update.password)
        user.sqlmodel_update(update_fields)
        user.add_to_db(session)
        return models.UserPrivate.model_validate(user)


@ app.patch('/users/{user_id}/admin/', responses={
    status.HTTP_401_UNAUTHORIZED: {'description': 'Invalid token', 'model': DetailOnlyResponse},
    status.HTTP_403_FORBIDDEN: {"description": 'User does not have permission to update this user', 'model': DetailOnlyResponse},
    status.HTTP_404_NOT_FOUND: {"description": models.User.not_found_message(), 'model': NotFoundResponse},
    status.HTTP_409_CONFLICT: {"description": 'Username or email already exists', 'model': DetailOnlyResponse},
})
async def patch_user_admin(
    user_id: models.UserTypes.id,
    user_update: models.UserUpdateAdmin,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(raise_exceptions=True, required_scopes={'admin'}))]
) -> models.User:

    with Session(c.db_engine) as session:
        user = models.User.get_one_by_id(session, user_id)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail=models.User.not_found_message())

        # if they changed their username, check if it's available
        if user_update.username != None:
            if user.username != user_update.username:
                response = await user_username_available(user_update.username)
                if response.available == False:
                    raise HTTPException(status.HTTP_409_CONFLICT,
                                        detail='Username already exists')
        # if they changed their email, check if it's available
        if user_update.email != None:
            if user.email != user_update.email:
                response = await user_email_available(user_update.email)
                if response.available == False:
                    raise HTTPException(status.HTTP_409_CONFLICT,
                                        detail='Email already exists')
        update_fields = {}
        if user_update.email != None:
            update_fields['email'] = user_update.email
        if user_update.username != None:
            update_fields['username'] = user_update.username
        if user_update.password != None:
            update_fields['hashed_password'] = utils.hash_password(
                user_update.password)
        if user_update.user_role_id != None:
            update_fields['user_role_id'] = user_update.user_role_id

        user.sqlmodel_update(update_fields)
        user.add_to_db(session)
        return user


@ app.delete('/users/{user_id}/', status_code=204, responses={
    status.HTTP_403_FORBIDDEN: {"description": 'User does not have permission to delete this user', 'model': DetailOnlyResponse},
    status.HTTP_404_NOT_FOUND: {
        "description": models.User.not_found_message(), 'model': NotFoundResponse}
}
)
async def delete_user(
    user_id: models.UserTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization())]
) -> Response:
    with Session(c.db_engine) as session:
        # make sure the user has permission to delete whoever user_id is
        # if user_id != auth_return.user.id:
        #     raise HTTPException(status.HTTP_403_FORBIDDEN,
        #                         detail='User does not have permission to delete this user')
        if models.User.delete_one_by_id(session, user_id) == 0:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail=models.User.not_found_message())
        else:
            return Response(status_code=204)


@ app.get('/users/{user_id}/sessions/', responses={status.HTTP_404_NOT_FOUND: {"description": models.User.not_found_message(), 'model': NotFoundResponse}})
async def get_user_sessions(
        user_id: models.UserTypes.id,
        authorization: typing.Annotated[GetAuthorizationReturn, Depends(get_authorization())]) -> list[models.AuthCredential]:

    with Session(c.db_engine) as session:

        print(authorization)

        if user_id != authorization.user.id:
            print('hello')
            raise auth.user_not_found_exception()

        user = models.User.get_one_by_id(session, user_id)
        if not user:
            if user_id != authorization.user.id:
                raise auth.user_not_found_exception()

        active_sessions = models.AuthCredential.get_all_by_key_values(
            session, {'user_id': user_id, 'type': 'access_token'})

        return active_sessions


# API Keys
@ app.get('/auth-credentials/{auth_credential_id}/', responses={status.HTTP_404_NOT_FOUND: {"description": models.AuthCredential.not_found_message(), 'model': NotFoundResponse}})
async def get_auth_credential(auth_credential_id: models.AuthCredentialTypes.id, authorization: typing.Annotated[GetAuthorizationReturn, Depends(get_authorization())]) -> models.AuthCredential:
    with Session(c.db_engine) as session:
        auth_credential = models.AuthCredential.get_one_by_id(
            session, auth_credential_id)
        if not auth_credential:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail=models.AuthCredential.not_found_message())
        return auth_credential


@ app.post('/auth-credentials/')
async def post_auth_credential(auth_credential_create: models.AuthCredentialCreate, authorization: typing.Annotated[GetAuthorizationReturn, Depends(get_authorization())]) -> models.AuthCredential:

    with Session(c.db_engine) as session:
        auth_credential = auth_credential_create.create()
        auth_credential.add_to_db(session)
        return auth_credential


@app.patch('/auth-credentials/{auth_credential_id}/')
async def patch_auth_credential(auth_credential_id: models.AuthCredentialTypes.id, auth_credential_update: models.AuthCredentialUpdate, authorization: typing.Annotated[GetAuthorizationReturn, Depends(get_authorization())]) -> models.AuthCredential:
    with Session(c.db_engine) as session:
        auth_credential = models.AuthCredential.get_one_by_id(
            session, auth_credential_id)
        if not auth_credential:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail=models.AuthCredential.not_found_message())

        auth_credential.sqlmodel_update(auth_credential_update)
        auth_credential.add_to_db(session)
        return auth_credential


@ app.delete('/auth-credentials/{auth_credential_id}/')
async def delete_auth_credential(auth_credential_id: models.AuthCredentialTypes.id, authorization: typing.Annotated[GetAuthorizationReturn, Depends(get_authorization())]) -> Response:

    with Session(c.db_engine) as session:
        if models.AuthCredential.delete_one_by_id(session, auth_credential_id) == 0:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail=models.AuthCredential.not_found_message())
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
        user = models.User.get_one_by_id(session, authorization.user.id)
        if user is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail=models.User.not_found_message())
        # convert user to models.UserPrivate
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
