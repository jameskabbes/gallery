from fastapi import FastAPI, HTTPException, Query, status, Response, Depends, Request, BackgroundTasks
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer, APIKeyHeader
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


class DetailOnlyResponse(BaseModel):
    detail: str


class NotFoundResponse(DetailOnlyResponse):
    pass


class ItemAvailableResponse(BaseModel):
    available: bool


# Authentication / Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token/", auto_error=False)


class GetAuthorizationReturn(BaseModel):
    isAuthorized: bool = False
    type: auth.BearerType | None = None
    exception: auth.EXCEPTION | None = None
    user: models.UserPrivate | None = None
    scopes: set[models.ScopeTypes.id] | None = None


class GetAuthorizationTokenReturn(GetAuthorizationReturn):
    type: auth.BearerType = 'token'


class GetAuthorizationAPIKeyReturn(GetAuthorizationReturn):
    type: auth.BearerType = 'api_key'


def get_authorization_from_bearer(
    bearer: auth.BearerString,
    required_scopes: set[models.ScopeTypes.id] = set(),
    expiry_timedelta: datetime.timedelta = typing.Annotated,
    raise_exceptions: bool = False,
    permitted_bearer_types: set[auth.BearerType] = auth.BEARER_TYPES,
    permitted_token_auth_sources: set[auth.TokenAuthSource] = auth.TOKEN_AUTH_SOURCES
) -> GetAuthorizationReturn:

    print('bearer', bearer)

    try:
        payload = jwt.decode(bearer, c.jwt_secret_key,
                             algorithms=[c.jwt_algorithm])

    except:
        print('111111')
        print('111111')
        print('111111')
        if raise_exceptions:
            raise auth.invalid_bearer_exception()
        return GetAuthorizationReturn(exception='invalid_bearer')

    if 'type' not in payload:
        return GetAuthorizationReturn(exception='missing_required_claims')

    bearer_type: auth.BearerType = payload['type']
    if bearer_type not in permitted_bearer_types:
        if raise_exceptions:
            raise auth.invalid_bearer_type_exception(
                bearer_type, permitted_bearer_types)
        else:
            return GetAuthorizationReturn(exception='invalid_bearer_type')

    if 'iat' not in payload:
        if raise_exceptions:
            raise auth.missing_required_claims_exception()
        return GetAuthorizationTokenReturn(exception='missing_required_claims')
    if 'exp' not in payload:
        if raise_exceptions:
            raise auth.missing_required_claims_exception()
        return GetAuthorizationTokenReturn(exception='missing_required_claims')

    dt_now = datetime.datetime.now(datetime.UTC)

    # check if built in dt_exp claim has expired
    dt_exp = datetime.datetime.fromtimestamp(
        payload.get('exp'), datetime.UTC)
    if dt_now > dt_exp:
        if raise_exceptions:
            raise auth.bearer_expired_exception()
        return GetAuthorizationTokenReturn(exception='bearer_expired')

    # check if built in dt_iat claim has expired given the expiry_timedelta
    dt_iat = datetime.datetime.fromtimestamp(
        payload.get('iat'), datetime.UTC)

    if dt_now > (dt_iat + expiry_timedelta):
        if raise_exceptions:
            raise auth.bearer_expired_exception()
        return GetAuthorizationTokenReturn(exception='bearer_expired')

    # for a token, check the auth source
    if bearer_type == 'token':
        if 'auth_source' not in payload:
            if raise_exceptions:
                raise auth.missing_required_claims_exception()
            return GetAuthorizationTokenReturn(exception='missing_required_claims')

        # make sure it is an allowed auth source
        auth_source: auth.TokenAuthSource = payload['auth_source']
        if auth_source not in permitted_token_auth_sources:
            if raise_exceptions:
                raise auth.invalid_token_exception()

            return GetAuthorizationTokenReturn(exception='invalid_token')

    scopes: set[models.ScopeTypes.id] = set()

    # token
    if bearer_type == 'token':

        user_id = models.User.import_from_jwt(payload).get('id')
        if not user_id:
            return GetAuthorizationTokenReturn(exception='missing_required_claims')

        with Session(c.db_engine) as session:
            user = models.User.get_one_by_id(session, user_id)
            if not user:
                return GetAuthorizationTokenReturn(exception='user_not_found')
            scopes = set([user_scope.scope.id for user_scope in user.scopes])

    # api_key
    elif bearer_type == 'api_key':
        api_key_id = models.APIKey.import_from_jwt(payload).get('id')
        if not api_key_id:
            return GetAuthorizationAPIKeyReturn(exception='missing_required_claims')

        with Session(c.db_engine) as session:
            api_key = models.APIKey.get_one_by_id(session, api_key_id)
            if not api_key:
                return GetAuthorizationAPIKeyReturn(exception='api_key_not_found')
            scopes = set(
                [api_key_scope.scope.id for api_key_scope in api_key.scopes])

    # check to see if the required scopes are in the scopes
    if not required_scopes.issubset(scopes):
        if raise_exceptions:
            raise auth.insufficient_scope_exception()
        return GetAuthorizationReturn(exception='insufficient_scope', type=bearer_type)

    return GetAuthorizationReturn(isAuthorized=True, type=bearer_type, user=models.UserPrivate.model_validate(user), scopes=scopes)


def get_authorization(
    required_scopes: set[str] = set(),
    expiry_timedelta: typing.Annotated[datetime.timedelta,
                                       'The timedelta from token creation in which the token is still valid'] = c.authentication['default_expiry_timedelta'],
    raise_exceptions: bool = False,
    permitted_bearer_types: set[auth.BearerType] = auth.BEARER_TYPES,
    permitted_token_auth_sources: set[auth.TokenAuthSource] = auth.TOKEN_AUTH_SOURCES
):
    def dependecy(bearer: typing.Annotated[auth.BearerString, Depends(oauth2_scheme)]):
        return get_authorization_from_bearer(
            bearer,
            required_scopes,
            expiry_timedelta,
            raise_exceptions,
            permitted_bearer_types,
            permitted_token_auth_sources)
    return dependecy


def make_token(user: models.UserBase,
               auth_source: auth.TokenAuthSource,
               expiry_timedelta: typing.Annotated[datetime.timedelta | None,
                                                  'The timedelta from token creation in which the token is still valid'] = c.authentication['default_expiry_timedelta'],
               expiry_datetime: typing.Annotated[datetime.datetime | None,
                                                 'The datetime at which the token will expire'] = None
               ) -> auth.Token:
    """make a new token for the given user"""

    dt_now: datetime.datetime = datetime.datetime.now(datetime.UTC)
    to_encode = {}
    to_encode.update({"type": 'token'})
    to_encode.update({"auth_source": auth_source})
    to_encode.update({"iat": dt_now.timestamp()})
    to_encode.update(user.export_to_jwt())

    if expiry_datetime == None and expiry_timedelta == None:
        raise ValueError(
            'Either expiry_timedelta or expiry_datetime must be provided')

    if expiry_datetime == None:
        expiry_datetime = dt_now + expiry_timedelta

    to_encode.update({"exp": expiry_datetime.timestamp()})

    return auth.Token(access_token=jwt.encode(to_encode, c.jwt_secret_key, algorithm=c.jwt_algorithm))


def make_api_key() -> auth.APIKey:
    return 'apikey1234'


async def authenticate_user_with_password(form_data: typing.Annotated[OAuth2PasswordRequestForm, Depends()]) -> models.User:
    with Session(c.db_engine) as session:
        user = models.User.authenticate(
            session, form_data.username, form_data.password)

        if not user:
            raise auth.credentials_exception()
        return user


@ app.post("/token/")
async def post_token(user: typing.Annotated[models.User, Depends(authenticate_user_with_password)]) -> auth.Token:
    return make_token(user, 'password')


class GetAuthenticationNestedReturn(BaseModel):
    user: models.UserPrivate | None = None
    exception: auth.EXCEPTION | None = None


assert c.root_config['auth_key'] == 'auth'


class GetAuthenticationReturn(BaseModel):
    auth: GetAuthenticationNestedReturn


def get_authentication(get_authorization_return: GetAuthorizationReturn) -> GetAuthenticationReturn:
    return GetAuthenticationReturn(auth=GetAuthenticationNestedReturn(user=get_authorization_return.user,
                                                                      exception=get_authorization_return.exception))


@ app.get('/auth/')
async def auth_root(authorization: typing.Annotated[GetAuthorizationReturn, Depends(get_authorization(raise_exceptions=False))]) -> GetAuthenticationReturn:
    return get_authentication(authorization)


class LoginResponse(GetAuthenticationReturn):
    token: auth.Token


@ app.post('/auth/login/password/', responses={status.HTTP_401_UNAUTHORIZED: {'description': 'Could not validate credentials', 'model': DetailOnlyResponse}})
async def login(user: typing.Annotated[models.User, Depends(authenticate_user_with_password)]) -> LoginResponse:
    return LoginResponse(
        auth=GetAuthenticationNestedReturn(
            user=models.UserPrivate.model_validate(user)),
        token=make_token(user, 'password')
    )


class GoogleAuthResponse(LoginResponse):
    pass


class GoogleAuthRequest(BaseModel):
    access_token: str


@ app.post("/auth/login/google/", responses={status.HTTP_400_BAD_REQUEST: {"description": 'Invalid token'}})
async def login_with_google(request_token: GoogleAuthRequest) -> GoogleAuthResponse:

    async with httpx.AsyncClient() as client:
        response = await client.get('https://www.googleapis.com/oauth2/v3/userinfo?access_token={}'.format(request_token.access_token))
        response.raise_for_status()
        user_info = response.json()

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

        return GoogleAuthResponse(
            auth=GetAuthenticationReturn(
                user=models.UserPrivate.model_validate(user)),
            token=make_token(user, 'google_oauth2')
        )


class LoginWithEmailMagicLinkRequest(BaseModel):
    email: models.UserTypes.email


def send_magic_link_to_email(model: LoginWithEmailMagicLinkRequest):
    with Session(c.db_engine) as session:
        user = models.User.get_one_by_key_values(
            session, {'email': model.email})
        if user:
            token = make_token(
                user, 'magic_link', expiry_timedelta=c.authentication['magic_link_expiry_timedelta'])
            print('beep boop beep... sending email')
            print('http://localhost:3000' +
                  c.root_config['magic_link_frontend_url'] + '?access_token=' + token.access_token)

    # still need to fill this function in!


@ app.post('/auth/login/email-magic-link/')
async def login_with_email_magic_link(model: LoginWithEmailMagicLinkRequest, background_tasks: BackgroundTasks) -> DetailOnlyResponse:
    background_tasks.add_task(send_magic_link_to_email, model)
    return DetailOnlyResponse(detail='If an account with this email exists, a login link has been sent.')


class VerifyMagicLinkRequest(BaseModel):
    access_token: str


@ app.post('/auth/verify-magic-link/', responses={status.HTTP_401_UNAUTHORIZED: {'description': 'Invalid token', 'model': DetailOnlyResponse}})
async def verify_magic_link(verify_magic_link_request: VerifyMagicLinkRequest) -> LoginResponse:

    authorization = get_authorization_from_bearer(
        verify_magic_link_request.access_token, expiry_timedelta=c.authentication['magic_link_expiry_timedelta'], raise_exceptions=True, permitted_bearer_types={'token'}, permitted_token_auth_sources={'magic_link'})

    return LoginResponse(
        auth=GetAuthenticationNestedReturn(
            user=authorization.user,
            exception=authorization.exception
        ),
        token=make_token(authorization.user, 'verified_magic_link')
    )


class SignupResponse(LoginResponse):
    pass


@ app.post('/auth/signup/', responses={status.HTTP_409_CONFLICT: {"description": 'User already exists', 'model': DetailOnlyResponse}})
async def sign_up(user_create: models.UserCreate) -> SignupResponse:

    user = await post_user(user_create)
    token = make_token(user, 'sign_up')

    return SignupResponse(
        auth=GetAuthenticationNestedReturn(user=user),
        token=token
    )

# USERS


@ app.get('/users/available/username/{username}/')
async def user_username_available(username: models.UserTypes.username) -> ItemAvailableResponse:
    with Session(c.db_engine) as session:
        return ItemAvailableResponse(available=models.User.is_username_available(session, username))


@ app.get('/users/available/email/{email}/')
async def user_email_available(email: models.UserTypes.email) -> ItemAvailableResponse:
    with Session(c.db_engine) as session:
        return ItemAvailableResponse(available=models.User.is_email_available(session, email))


@ app.get('/users/username/{username}', responses={status.HTTP_404_NOT_FOUND: {"description": models.User.not_found_message(), 'model': NotFoundResponse}})
async def get_user_by_username(username: models.UserTypes.username) -> models.UserPublic:
    with Session(c.db_engine) as session:
        user = models.User.get_one_by_key_values(
            session, {'username': username})
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail=models.User.not_found_message())
        else:
            return models.UserPublic.model_validate(user)


@ app.get('/users/{user_id}', responses={status.HTTP_404_NOT_FOUND: {"description": models.User.not_found_message(), 'model': NotFoundResponse}})
async def get_user_by_id(user_id: models.UserTypes.id) -> models.UserPublic:
    with Session(c.db_engine) as session:
        user = models.User.get_one_by_id(session, user_id)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail=models.User.not_found_message())
        else:
            return models.UserPublic.model_validate(user)


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
        get_authorization(raise_exceptions=True, required_scopes={
        }))]
) -> models.UserPrivate:

    print(authorization)
    with Session(c.db_engine) as session:
        user = models.User.get_one_by_id(session, user_id)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail=models.User.not_found_message())

        # check if the user has permission to update this specific user

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


@ app.delete('/users/{user_id}/', status_code=204, responses={
    status.HTTP_403_FORBIDDEN: {"description": 'User does not have permission to delete this user', 'model': DetailOnlyResponse},
    status.HTTP_404_NOT_FOUND: {
        "description": models.User.not_found_message(), 'model': NotFoundResponse}
}
)
async def delete_user(
    user_id: models.UserTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(raise_exceptions=True, required_scopes={
        }))]
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
class GetProfilePageResponse(GetAuthenticationReturn):
    user: models.UserPrivate | None = None


@ app.get('/profile/page/')
async def get_pages_profile(authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization(raise_exceptions=True, permitted_bearer_types={'token'}))]) -> GetProfilePageResponse:

    with Session(c.db_engine) as session:
        user = models.User.get_one_by_id(session, authorization.user.id)
        if user is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail=models.User.not_found_message())
        # convert user to models.UserPrivate
        return GetProfilePageResponse(
            auth=get_authentication(authorization),
            user=models.UserPrivate.model_validate(user)
        )


class GetHomePageResponse(GetAuthenticationReturn):
    pass


@ app.get('/home/page/')
async def get_home_page(authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        get_authorization())]) -> GetHomePageResponse:

    return GetHomePageResponse(
        auth=get_authentication(authorization)
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
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
