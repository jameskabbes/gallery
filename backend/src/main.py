from fastapi import FastAPI, HTTPException, Query, status, Response, Depends, Request
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
import logging

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


# set up authentication methods
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token/", auto_error=False)


class GetAuthorizationReturn(BaseModel):
    isAuthenticated: bool = False
    exception: auth.EXCEPTION | None = None
    user: models.UserPrivate | None = None


def get_authorization(required_scopes: set[str] = set(), expiry_timedelta: typing.Annotated[datetime.timedelta, 'The timedelta from token creation in which the token is still valid'] = c.authentication['default_expiry_timedelta'], raise_exceptions: bool = False):
    def dependecy(authorization_bearer_header: typing.Annotated[str, Depends(oauth2_scheme)]):

        try:
            payload = jwt.decode(authorization_bearer_header, c.jwt_secret_key,
                                 algorithms=[c.jwt_algorithm])
        except:
            if raise_exceptions:
                raise auth.INVALID_BEARER_EXCEPTION
            return GetAuthorizationReturn(exception='invalid_bearer')

        if 'type' not in payload:
            return GetAuthorizationReturn(exception='missing_required_claims')

        ###

        return GetAuthorizationReturn(payload=payload, type=payload['type'])

    return dependecy


#

def make_token(user: models.UserBase, expiry_datetime: typing.Annotated[typing.Optional[datetime.timedelta], 'The datetime the token expires'] = None) -> str:

    dt_now: datetime.datetime = datetime.datetime.now(datetime.UTC)
    to_encode = {}
    to_encode.update(user.export_for_token_payload())
    to_encode.update({"iat": dt_now.timestamp()})
    if expiry_datetime != None:
        to_encode.update({"exp": (dt_now + expiry_datetime).timestamp()})

    return jwt.encode(to_encode, c.jwt_secret_key, algorithm=c.jwt_algorithm)


@ app.post('/test/')
async def test(authorization: typing.Annotated[GetAuthorizationReturn, Depends(get_authorization(raise_exceptions=True))]):

    print(authorization)
    return {'asd': 'asd'}


# @ app.post("/token/")
# async def post_token(
#     form_data: typing.Annotated[OAuth2PasswordRequestForm, Depends()],
# ) -> models.Token:
#     with Session(c.db_engine) as session:
#         user = models.User.authenticate(
#             session, form_data.username, form_data.password)
#         if not user:
#             raise auth.CREDENTIALS_EXCEPTION
#         access_token = make_token(user)
#         return models.Token(access_token=access_token)
# assert c.root_config['auth_key'] == 'auth'
# class AuthResponse(BaseModel):
#     auth: GetAuthReturn
# class LoginResponse(AuthResponse):
#     token: models.Token
# @ app.post('/auth/login/password/', responses={status.HTTP_401_UNAUTHORIZED: {'description': 'Could not validate credentials', 'model': DetailOnlyResponse}})
# async def login(form_data: typing.Annotated[OAuth2PasswordRequestForm, Depends()]) -> LoginResponse:
#     with Session(c.db_engine) as session:
#         email = form_data.username
#         password = form_data.password
#         user = models.User.authenticate(
#             session, email, password)
#         if not user:
#             raise auth.CREDENTIALS_EXCEPTION
#         access_token = create_access_token(
#             data=user.export_for_token_payload())
#         return LoginResponse(
#             auth=GetAuthReturn(user=models.UserPublic.model_validate(user)),
#             token=models.Token(access_token=access_token)
#         )
# class GoogleAuthResponse(LoginResponse):
#     pass
# class GoogleAuthRequest(BaseModel):
#     access_token: str
# @app.post("/auth/login/google/", responses={status.HTTP_400_BAD_REQUEST: {"description": 'Invalid token'}})
# async def login_with_google(request_token: GoogleAuthRequest) -> GoogleAuthResponse:
#     # call https://www.googleapis.com/oauth2/v3/userinfo?access_token=
#     async with httpx.AsyncClient() as client:
#         response = await client.get('https://www.googleapis.com/oauth2/v3/userinfo?access_token={}'.format(request_token.access_token))
#         response.raise_for_status()
#         user_info = response.json()
#     # fields: sub, name, given_name, family_name, picture, email, email_verified
#     email = user_info.get('email')
#     if not email:
#         raise HTTPException(status.HTTP_400_BAD_REQUEST,
#                             detail='Invalid token')
#     with Session(c.db_engine) as session:
#         user = models.User.get_one_by_key_values(session, {'email': email})
#         if not user:
#             user_create = models.UserCreate(
#                 email=email,
#             )
#             user = user_create.create()
#             user.add_to_db(session)
#         access_token = create_access_token(
#             data=user.export_for_token_payload())
#         return GoogleAuthResponse(
#             auth=GetAuthReturn(user=models.UserPrivate.model_validate(user)),
#             token=models.Token(access_token=access_token)
#         )
# class LoginWithEmailMagicLinkRequest(BaseModel):
#     email: models.UserTypes.email
# async def send_magic_link_email(model: LoginWithEmailMagicLinkRequest):
#     with Session(c.db_engine) as session:
#         user = models.User.get_one_by_key_values(
#             session, {'email': model.email})
#         if user:
#             access_token = create_access_token(
#                 data=user.export_for_token_payload())
#             pass
# @app.post('auth/login/email-magic-link/')
# async def login_with_email_magic_link(model: LoginWithEmailMagicLinkRequest) -> DetailOnlyResponse:
#     send_magic_link_email(model)
#     return DetailOnlyResponse(detail='If an account with this email exists, a login link has been sent.')
# @app.get('/auth/verify-magic-link', responses={status.HTTP_401_UNAUTHORIZED: {'description': 'Invalid token', 'model': DetailOnlyResponse}})
# async def verify_magic_link(token: str) -> LoginResponse:
#     pass
# class SignupResponse(AuthResponse):
#     user: models.UserPrivate
#     token: models.Token
# @ app.post('auth/signup/', responses={status.HTTP_409_CONFLICT: {"description": 'User already exists', 'model': DetailOnlyResponse}})
# async def sign_up(user_create: models.UserCreate) -> SignupResponse:
#     user = await post_user(user_create)
#     access_token = create_access_token(data=user.export_for_token_payload())
#     return SignupResponse(
#         auth=GetAuthReturn(user=models.UserPublic.model_validate(user)),
#         user=user,
#         token=models.Token(access_token=access_token)
#     )
# # Token / api_key
# # USERS
# @ app.get('/users/available/username/{username}/')
# async def user_username_available(username: models.UserTypes.username) -> ItemAvailableResponse:
#     with Session(c.db_engine) as session:
#         if len(username) < 1:
#             return ItemAvailableResponse(available=False)
#         with Session(c.db_engine) as session:
#             if session.exec(select(models.User).where(models.User.username == username)).first():
#                 return ItemAvailableResponse(available=False)
#             else:
#                 return ItemAvailableResponse(available=True)
# @ app.get('/users/available/email/{email}/')
# async def user_email_available(email: models.UserTypes.email) -> ItemAvailableResponse:
#     with Session(c.db_engine) as session:
#         if models.User.get_one_by_key_values(session, {'email': email}) == None:
#             return ItemAvailableResponse(available=True)
#         else:
#             return ItemAvailableResponse(available=False)
# @app.get('/users/{user_id}', responses={status.HTTP_404_NOT_FOUND: {"description": models.User.not_found_message(), 'model': NotFoundResponse}})
# async def get_user_by_id(user_id: models.UserTypes.id) -> models.UserPublic:
#     with Session(c.db_engine) as session:
#         user = models.User.get_one_by_id(session, user_id)
#         if not user:
#             raise HTTPException(status.HTTP_404_NOT_FOUND,
#                                 detail=models.User.not_found_message())
#         else:
#             return models.UserPublic.model_validate(user)
# @app.get('/users/username/{username}', responses={status.HTTP_404_NOT_FOUND: {"description": models.User.not_found_message(), 'model': NotFoundResponse}})
# async def get_user_by_username(username: models.UserTypes.username) -> models.UserPublic:
#     with Session(c.db_engine) as session:
#         user = models.User.get_one_by_key_values(
#             session, {'username': username})
#         if not user:
#             raise HTTPException(status.HTTP_404_NOT_FOUND,
#                                 detail=models.User.not_found_message())
#         else:
#             return models.UserPublic.model_validate(user)
# @ app.post('/users/', responses={status.HTTP_409_CONFLICT: {"description": 'User already exists', 'model': DetailOnlyResponse}})
# async def post_user(user_create: models.UserCreate) -> models.UserPrivate:
#     with Session(c.db_engine) as session:
#         # see if the email is available
#         resp = await user_email_available(user_create.email)
#         if not resp.available:
#             raise HTTPException(
#                 status_code=status.HTTP_409_CONFLICT, detail='User already exists')
#         user = user_create.create()
#         user.add_to_db(session)
#         return models.UserPrivate.model_validate(user)
# @ app.patch('/users/{user_id}/', responses={
#     status.HTTP_401_UNAUTHORIZED: {'description': 'Invalid token', 'model': DetailOnlyResponse},
#     status.HTTP_403_FORBIDDEN: {"description": 'User does not have permission to update this user', 'model': DetailOnlyResponse},
#     status.HTTP_404_NOT_FOUND: {"description": models.User.not_found_message(), 'model': NotFoundResponse},
#     status.HTTP_409_CONFLICT: {"description": 'Username or email already exists', 'model': DetailOnlyResponse},
# })
# async def patch_user(user_id: models.UserTypes.id, user_update: models.UserUpdate, decoded_bearer: typing.Annotated[DecodeBearerReturn, Depends(decode_bearer)]) -> models.UserPrivate:
#     if decoded_bearer.exception:
#         raise auth.EXCEPTION_MAPPING[decoded_bearer.exception]
#     if decoded_bearer.type == 'token':
#     if decoded_bearer.type == 'token':
#         if decoded_bearer.token.exception != None:
#             raise auth.EXCEPTION_MAPPING[decoded_bearer.token.exception]
#         if user_id != decoded_bearer.token.user.id:
#             raise HTTPException(status.HTTP_403_FORBIDDEN,
#                                 detail='User does not have permission to update this user')
#     auth_return = await get_auth(token_return)
#     if auth_return.exception:
#         raise auth.EXCEPTION_MAPPING[auth_return.exception]
#     with Session(c.db_engine) as session:
#         user = models.User.get_one_by_id(session, user_id)
#         if not user:
#             raise HTTPException(status.HTTP_404_NOT_FOUND,
#                                 detail=models.User.not_found_message())
#         if user.id != auth_return.user.id:
#             raise HTTPException(status.HTTP_403_FORBIDDEN,
#                                 detail='User does not have permission to update this user')
#         # if they changed their username, check if it's available
#         if user_update.username != None:
#             if user.username != user_update.username:
#                 response = await user_username_available(user_update.username)
#                 if response.available == False:
#                     raise HTTPException(status.HTTP_409_CONFLICT,
#                                         detail='Username already exists')
#         # if they changed their email, check if it's available
#         if user_update.email != None:
#             if user.email != user_update.email:
#                 response = await user_email_available(user_update.email)
#                 if response.available == False:
#                     raise HTTPException(status.HTTP_409_CONFLICT,
#                                         detail='Email already exists')
#         update_fields = {}
#         if user_update.email != None:
#             update_fields['email'] = user_update.email
#         if user_update.username != None:
#             update_fields['username'] = user_update.username
#         if user_update.password != None:
#             update_fields['hashed_password'] = utils.hash_password(
#                 user_update.password)
#         user.sqlmodel_update(update_fields)
#         user.add_to_db(session)
#         return models.UserPrivate.model_validate(user)
# @ app.delete('/users/{user_id}/', status_code=204, responses={
#     status.HTTP_403_FORBIDDEN: {"description": 'User does not have permission to delete this user', 'model': DetailOnlyResponse},
#     status.HTTP_404_NOT_FOUND: {
#         "description": models.User.not_found_message(), 'model': NotFoundResponse}
# }
# )
# async def delete_user(user_id: models.UserTypes.id, token_return: typing.Annotated[GetTokenReturn, Depends(get_token)]) -> Response:
#     auth_return = await get_auth(token_return, expiry_timedelta=datetime.timedelta(minutes=5))
#     if auth_return.exception:
#         raise auth.EXCEPTION_MAPPING[auth_return.exception]
#     with Session(c.db_engine) as session:
#         if user_id != auth_return.user.id:
#             raise HTTPException(status.HTTP_403_FORBIDDEN,
#                                 detail='User does not have permission to delete this user')
#         if models.User.delete_one_by_id(session, user_id) == 0:
#             raise HTTPException(status.HTTP_404_NOT_FOUND,
#                                 detail=models.User.not_found_message())
#         else:
#             return Response(status_code=204)
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
# # Page
# class GetProfilePageResponse(AuthResponse):
#     user: models.UserPrivate | None = None
# @ app.get('/profile/page/')
# async def get_pages_profile(token_return: typing.Annotated[GetTokenReturn, Depends(get_token)]) -> GetProfilePageResponse:
#     auth_return = await get_auth(token_return)
#     if auth_return.exception:
#         raise auth.EXCEPTION_MAPPING[auth_return.exception]
#     with Session(c.db_engine) as session:
#         user = models.User.get_one_by_id(session, auth_return.user.id)
#         if user is None:
#             raise HTTPException(status.HTTP_404_NOT_FOUND,
#                                 detail=models.User.not_found_message())
#         # convert user to models.UserPrivate
#         return GetProfilePageResponse(
#             auth=auth_return,
#             user=models.UserPrivate.model_validate(user)
#         )
# class GetHomePageResponse(AuthResponse):
#     pass
# @ app.get('/home/page/')
# async def get_home_page(token_return: typing.Annotated[GetTokenReturn, Depends(get_token)]) -> GetHomePageResponse:
#     auth_return = await get_auth(token_return)
#     return GetHomePageResponse(
#         auth=auth_return
#     )
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
