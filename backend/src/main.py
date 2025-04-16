import uvicorn
from fastapi import FastAPI, HTTPException, Query, status, Response, Depends, Request, BackgroundTasks, Form, File, UploadFile, APIRouter, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from sqlalchemy import and_
from sqlalchemy.orm import selectinload, Session
from sqlalchemy.sql import func, select
from gallery import models, utils, auth, client, types, config
from gallery.config import constants, settings
from gallery.models import api_key_scope, api_key, file, gallery_permission, gallery, image_file_metadata, image_version, otp, sign_up, user_access_token, user

import datetime
import typing
import httpx
from jwt.exceptions import InvalidTokenError, MissingRequiredClaimError, DecodeError
from pydantic import BaseModel, model_validator
import datetime
from functools import wraps
from urllib.parse import urlencode
import shutil
from google.oauth2 import id_token
from google.auth.transport import requests


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('startingup')
    yield
    print('closingdown')

app = FastAPI(lifespan=lifespan)
c = client.Client(config={})


def get_pagination(max_limit: int = 100, default_limit: int = 10):
    def dependency(limit: int = Query(default_limit, ge=1, le=max_limit, description='Quantity of results'), offset: int = Query(0, ge=0, description='Index of the first result')):
        return models.Pagination(limit=limit, offset=offset)
    return dependency


# Users
user_router = APIRouter(
    prefix='/users', tags=[models.User._ROUTER_TAG])
user_admin_router = APIRouter(
    prefix='/admin/users', tags=[models.User._ROUTER_TAG, 'Admin'])


@user_router.get('/me/', responses=models.User.get_responses())
async def get_user_me(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())]
) -> models.User.Private:
    return models.UserPrivate.model_validate(authorization.user)


@user_router.get('/{user_id}/', responses=models.User.get_responses())
async def get_user_by_id(
    user_id: models.UserTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(raise_exceptions=False))]
) -> models.UserPublic:
    async with c.AsyncSession() as session:
        return models.UserPublic.model_validate(await models.User.api_get(models.User.GetParams.model_construct(
            session=session, c=c, authorized_user_id=authorization._user_id, id=user_id)))


@user_admin_router.get('/{user_id}/', responses=models.User.get_responses())
async def get_user_by_id_admin(
    user_id: models.UserTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))]
) -> models.User:
    async with c.AsyncSession() as session:
        a = await models.User.api_get(models.User.GetParams.model_construct(session=session, c=c, authorized_user_id=authorization._user_id, id=user_id, admin=True))


@user_admin_router.post('/', responses=models.User.post_responses())
async def post_user_admin(
    user_create_admin: models.UserAdminCreate,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))]
) -> models.User:
    async with c.AsyncSession() as session:
        return await models.User.api_post(models.User.PostParams.model_construct(session=session, c=c, authorized_user_id=authorization._user_id, admin=True, create_model=user_create_admin))


@user_router.patch('/me/', responses=models.User.patch_responses())
async def patch_self(
    user_update: models.UserUpdate,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())]
) -> models.UserPrivate:
    async with c.AsyncSession() as session:
        return models.UserPrivate.model_validate(await models.User.api_patch(models.User.PatchParams.model_construct(session=session, c=c, authorized_user_id=authorization._user_id, id=authorization._user_id, update_model=models.UserAdminUpdate(**user_update.model_dump(exclude_unset=True)))))


@user_admin_router.patch('/{user_id}/', responses=models.User.patch_responses())
async def patch_user_admin(
    user_id: models.UserTypes.id,
    user_update_admin: models.UserAdminUpdate,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))]
) -> models.User:
    async with c.AsyncSession() as session:
        return await models.User.api_patch(models.User.PatchParams.model_construct(session=session, c=c, authorized_user_id=authorization._user_id, id=user_id, admin=True, update_model=user_update_admin))


@user_router.delete('/me/', responses=models.User.delete_responses(), status_code=status.HTTP_204_NO_CONTENT)
async def delete_self(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())]
):
    async with c.AsyncSession() as session:
        return await models.User.api_delete(models.User.DeleteParams.model_construct(
            session=session, c=c, authorized_user_id=authorization._user_id, id=authorization._user_id))


@user_admin_router.delete('/{user_id}/', responses=models.User.delete_responses(), status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_admin(
    user_id: models.UserTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))]
):
    async with c.AsyncSession() as session:
        return await models.User.api_delete(models.User.DeleteParams.model_construct(
            session=session, c=c, authorized_user_id=authorization._user_id, id=user_id, admin=True))


@user_router.get('/', responses=models.User.post_responses())
async def get_users(
    pagination: typing.Annotated[models.Pagination, Depends(get_pagination())]
) -> list[models.UserPublic]:

    async with c.AsyncSession() as session:
        query = select(models.User).where(
            models.User.username != None)
        query = models.build_pagination(query, pagination)
        users = session.exec(query).all()
        return [models.UserPublic.model_validate(user) for user in users]


@user_admin_router.get('/')
async def get_users_admin(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))],
    pagination: typing.Annotated[models.Pagination, Depends(get_pagination())]
) -> list[models.User]:

    async with c.AsyncSession() as session:
        query = select(models.User)
        query = models.build_pagination(query, pagination)
        users = session.exec(query).all()
        return users


@user_router.get('/available/username/{username}/',
                 responses={status.HTTP_409_CONFLICT: {
                     "description": 'Username already exists', 'model': DetailOnlyResponse}})
async def get_user_username_available(username: models.UserTypes.username):
    async with c.AsyncSession() as session:
        return await models.User.api_get_is_username_available(session, username)


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
        make_get_auth_dependency())]
) -> models.UserAccessToken:
    async with c.AsyncSession() as session:
        return await models.UserAccessToken.api_get(models.UserAccessToken.GetParams.model_construct(
            session=session, c=c, authorized_user_id=authorization._user_id, id=user_access_token_id))


@user_access_token_admin_router.get('/{user_access_token_id}/', responses=models.UserAccessToken.get_responses())
async def get_user_access_token_by_id_admin(
    user_access_token_id: models.UserAccessTokenTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))]
) -> models.UserAccessToken:
    async with c.AsyncSession() as session:
        return await models.UserAccessToken.api_get(models.UserAccessToken.GetParams.model_construct(
            session=session, c=c, authorized_user_id=authorization._user_id, id=user_access_token_id, admin=True))


@user_access_token_admin_router.post('/', responses=models.UserAccessToken.post_responses())
async def post_user_access_token_admin(
    user_access_token_create_admin: models.UserAccessTokenAdminCreate,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))]
) -> models.UserAccessToken:
    async with c.AsyncSession() as session:
        return await models.UserAccessToken.api_post(models.UserAccessToken.PostParams.model_construct(
            session=session, c=c, authorized_user_id=authorization._user_id, admin=True, create_model=user_access_token_create_admin))


@user_access_token_router.delete('/{user_access_token_id}/', responses=models.UserAccessToken.delete_responses(), status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_access_token(
    user_access_token_id: models.UserAccessTokenTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())]
):
    async with c.AsyncSession() as session:
        return await models.UserAccessToken.api_delete(models.UserAccessToken.DeleteParams.model_construct(
            session=session, c=c, authorized_user_id=authorization._user_id, id=user_access_token_id))


@user_access_token_admin_router.delete('/{user_access_token_id}/', responses=models.UserAccessToken.delete_responses(), status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_access_token_admin(
    user_access_token_id: models.UserAccessTokenTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))]
):
    async with c.AsyncSession() as session:
        return await models.UserAccessToken.api_delete(models.UserAccessToken.DeleteParams.model_construct(
            session=session, c=c, authorized_user_id=authorization._user_id, id=user_access_token_id, admin=True))


WrongUserPermissionUserAccessToken = HTTPException(
    status.HTTP_403_FORBIDDEN, detail='User does not have permission to view another user\'s access tokens')


def user_access_token_pagination(
    pagination: typing.Annotated[models.Pagination, Depends(
        get_pagination(default_limit=50, max_limit=500))]
):
    return pagination


@user_access_token_router.get('/', tags=[models.User._ROUTER_TAG], responses={status.HTTP_404_NOT_FOUND: {"description": models.User.not_found_message(), 'model': NotFoundResponse}, WrongUserPermissionUserAccessToken.status_code: {'description': WrongUserPermissionUserAccessToken.detail, 'model': DetailOnlyResponse}})
async def get_user_access_tokens(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())],
    pagination: models.Pagination = Depends(user_access_token_pagination)

) -> list[models.UserAccessToken]:
    async with c.AsyncSession() as session:
        query = select(models.UserAccessToken).where(
            models.UserAccessToken.user_id == authorization._user_id)
        query = models.build_pagination(query, pagination)
        user_access_tokens = session.exec(query).all()
        return user_access_tokens


@user_access_token_admin_router.get('/users/{user_id}/', tags=[models.User._ROUTER_TAG], responses={status.HTTP_404_NOT_FOUND: {"description": models.User.not_found_message(), 'model': NotFoundResponse}})
async def get_user_access_tokens_admin(
    user_id: models.UserTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))],
    pagination: models.Pagination = Depends(user_access_token_pagination)
) -> list[models.UserAccessToken]:
    async with c.AsyncSession() as session:

        query = select(models.UserAccessToken).where(
            models.UserAccessToken.user_id == user_id)
        query = models.build_pagination(query, pagination)
        user_access_tokens = session.exec(query).all()
        return user_access_tokens


@user_access_token_router.get('/details/count/')
async def get_user_access_tokens_count(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())],
) -> int:
    async with c.AsyncSession() as session:
        query = select(func.count()).select_from(models.UserAccessToken).where(
            models.UserAccessToken.user_id == authorization._user_id)
        return session.exec(query).one()


app.include_router(user_access_token_router)
app.include_router(user_access_token_admin_router)


# API Keys


api_key_router = APIRouter(
    prefix='/api-keys', tags=[models.ApiKey._ROUTER_TAG])
api_key_admin_router = APIRouter(
    prefix='/admin/api-keys', tags=[models.ApiKey._ROUTER_TAG, 'Admin'])


@api_key_router.get('/{api_key_id}/', responses=models.ApiKey.get_responses())
async def get_api_key_by_id(
    api_key_id: models.ApiKeyTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())]
) -> models.ApiKeyPrivate:
    async with c.AsyncSession() as session:
        return models.ApiKeyPrivate.model_validate(await models.ApiKey.api_get(models.ApiKey.GetParams.model_construct(
            session=session, c=c, authorized_user_id=authorization._user_id, id=api_key_id)))


@api_key_admin_router.get('/{api_key_id}/', responses=models.ApiKey.get_responses())
async def get_api_key_by_id_admin(
    api_key_id: models.ApiKeyTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))]
) -> models.ApiKey:
    async with c.AsyncSession() as session:
        return await models.ApiKey.api_get(models.ApiKey.GetParams.model_construct(
            session=session, c=c, authorized_user_id=authorization._user_id, id=api_key_id, admin=True))


@api_key_router.post('/', responses=models.ApiKey.post_responses())
async def post_api_key_to_user(
    api_key_create: models.ApiKeyCreate,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())]
) -> models.ApiKeyPrivate:

    async with c.AsyncSession() as session:
        return models.ApiKeyPrivate.from_api_key(await models.ApiKey.api_post(models.ApiKey.PostParams.model_construct(session=session, c=c, authorized_user_id=authorization._user_id, create_model=models.ApiKeyAdminCreate(
            **api_key_create.model_dump(exclude_unset=True), user_id=authorization._user_id)))
        )


@api_key_admin_router.post('/', responses=models.ApiKey.post_responses())
async def post_api_key_to_user_admin(
    api_key_create_admin: models.ApiKeyAdminCreate,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))]
) -> models.ApiKey:
    async with c.AsyncSession() as session:
        return await models.ApiKey.api_post(models.ApiKey.PostParams.model_construct(session=session, c=c, authorized_user_id=authorization._user_id, admin=True, create_model=models.ApiKeyAdminCreate(**api_key_create_admin.model_dump(exclude_unset=True))))


@api_key_router.patch('/{api_key_id}/', responses=models.ApiKey.patch_responses())
async def patch_api_key(
    api_key_id: models.ApiKeyTypes.id,
    api_key_update: models.ApiKeyUpdate,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())]
) -> models.ApiKeyPrivate:
    async with c.AsyncSession() as session:
        return models.ApiKeyPrivate.from_api_key(await models.ApiKey.api_patch(models.ApiKey.PatchParams.model_construct(
            session=session, c=c, authorized_user_id=authorization._user_id, id=api_key_id, update_model=models.ApiKeyAdminUpdate(**api_key_update.model_dump(exclude_unset=True)))))


@api_key_admin_router.patch('/{api_key_id}/', responses=models.ApiKey.patch_responses())
async def patch_api_key_admin(
    api_key_id: models.ApiKeyTypes.id,
    api_key_update_admin: models.ApiKeyAdminUpdate,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))]
) -> models.ApiKey:
    async with c.AsyncSession() as session:
        return await models.ApiKey.api_patch(models.ApiKey.PatchParams.model_construct(
            session=session, c=c, authorized_user_id=authorization._user_id, id=api_key_id, admin=True, update_model=models.ApiKeyAdminUpdate(**api_key_update_admin.model_dump(exclude_unset=True))))


@api_key_router.delete('/{api_key_id}/', responses=models.ApiKey.delete_responses(), status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    api_key_id: models.ApiKeyTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())]
):
    async with c.AsyncSession() as session:
        return await models.ApiKey.api_delete(models.ApiKey.DeleteParams.model_construct(
            session=session, c=c, authorized_user_id=authorization._user_id, id=api_key_id))


@api_key_admin_router.delete('/{api_key_id}/', responses=models.ApiKey.delete_responses(), status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key_admin(
    api_key_id: models.ApiKeyTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))]
):
    async with c.AsyncSession() as session:
        return await models.ApiKey.api_delete(models.ApiKey.DeleteParams.model_construct(
            session=session, c=c, authorized_user_id=authorization._user_id, id=api_key_id, admin=True))


class ApiKeyJWTResponse(BaseModel):
    jwt: str


@api_key_router.get('/{api_key_id}/generate-jwt/', responses={status.HTTP_404_NOT_FOUND: {"description": models.ApiKey.not_found_message(), 'model': NotFoundResponse}})
async def get_api_key_jwt(
    api_key_id: models.ApiKeyTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())]
) -> ApiKeyJWTResponse:
    async with c.AsyncSession() as session:
        api_key = await models.ApiKey.api_get(models.ApiKey.GetParams.model_construct(session=session, c=c, authorized_user_id=authorization._user_id, id=api_key_id))
        return ApiKeyJWTResponse(
            jwt=c.jwt_encode(api_key.encode())
        )

UserNotPermittedToViewAnotherUserApiKeys = HTTPException(
    status.HTTP_403_FORBIDDEN, detail='User does not have permission to view another user\'s API keys')


class GetApiKeysQueryParamsReturn(BaseModel):
    pagination: models.Pagination
    order_bys: list[models.OrderBy[models.ApiKeyTypes.order_by]]


def get_api_keys_query_params(
        pagination: typing.Annotated[models.Pagination, Depends(get_pagination())],
        order_bys: typing.Annotated[list[models.OrderBy[models.ApiKeyTypes.order_by]], Depends(models.ApiKey.make_order_by_dependency())]):
    return GetApiKeysQueryParamsReturn(pagination=pagination, order_bys=order_bys)


@api_key_router.get('/')
async def get_user_api_keys(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())],
    get_api_keys_query_params: GetApiKeysQueryParamsReturn = Depends(
        get_api_keys_query_params)
) -> list[models.ApiKeyPrivate]:
    async with c.AsyncSession() as session:

        query = select(models.ApiKey).options(selectinload(models.ApiKey.api_key_scopes)).where(
            models.ApiKey.user_id == authorization._user_id)
        query = models.build_pagination(
            query, get_api_keys_query_params.pagination)
        query = models.ApiKey._build_order_by(
            query, get_api_keys_query_params.order_bys)

        user_api_keys = session.exec(query).all()
        return [models.ApiKeyPrivate.from_api_key(api_key) for api_key in user_api_keys]


@api_key_router.get('/details/count/')
async def get_user_api_keys_count(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())],
) -> int:
    async with c.AsyncSession() as session:
        query = select(func.count()).select_from(models.ApiKey).where(
            models.ApiKey.user_id == authorization._user_id)
        return session.exec(query).one()


@api_key_admin_router.get('/users/{user_id}/', tags=[models.User._ROUTER_TAG])
async def get_user_api_keys_admin(
    user_id: models.UserTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))],
    get_api_keys_query_params: GetApiKeysQueryParamsReturn = Depends(
        get_api_keys_query_params)
) -> list[models.ApiKey]:
    async with c.AsyncSession() as session:

        query = select(models.ApiKey).where(
            models.ApiKey.user_id == user_id)
        query = models.build_pagination(
            query, get_api_keys_query_params.pagination)
        query = models.ApiKey._build_order_by(
            query, get_api_keys_query_params.order_bys)

        user_api_keys = session.exec(query).all()
        return user_api_keys


@api_key_router.get('/details/available/', responses={status.HTTP_409_CONFLICT: {"description": models.ApiKey.already_exists_message(), 'model': DetailOnlyResponse}})
async def get_api_key_available(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())],
    api_key_available: models.ApiKeyAvailable = Depends(),
):
    async with c.AsyncSession() as session:
        await models.ApiKey.api_get_is_available(session, models.ApiKeyAdminAvailable(
            **api_key_available.model_dump(exclude_unset=True), user_id=authorization._user_id
        ))


@api_key_admin_router.get('/details/available/', responses={status.HTTP_409_CONFLICT: {"description": models.ApiKey.already_exists_message(), 'model': DetailOnlyResponse}})
async def get_api_key_available_admin(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))],
    api_key_available_admin: models.ApiKeyAdminAvailable = Depends(),
):
    async with c.AsyncSession() as session:
        await models.ApiKey.api_get_is_available(session, api_key_available_admin)


app.include_router(api_key_router)
app.include_router(api_key_admin_router)


# API Key Scope


api_key_scope_router = APIRouter(
    prefix='/api-key-scopes', tags=[models.ApiKeyScope._ROUTER_TAG])
api_key_scope_admin_router = APIRouter(
    prefix='/admin/api-key-scopes', tags=[models.ApiKeyScope._ROUTER_TAG, 'Admin'])


@api_key_scope_router.post('/api-keys/{api_key_id}/scopes/{scope_id}/',
                           responses={status.HTTP_404_NOT_FOUND: {
                               "description": models.ApiKey.not_found_message(), 'model': NotFoundResponse}},
                           )
@api_key_scope_admin_router.post('/api-keys/{api_key_id}/scopes/{scope_id}/',
                                 responses={status.HTTP_404_NOT_FOUND: {
                                     "description": models.ApiKey.not_found_message(), 'model': NotFoundResponse}},
                                 )
async def add_scope_to_api_key_admin(
    api_key_id: models.ApiKeyTypes.id,
    scope_id: types.ScopeTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))]
):
    async with c.AsyncSession() as session:
        return await models.ApiKeyScope.api_post(models.ApiKeyScope.PostParams.model_construct(session=session, c=c, authorized_user_id=authorization._user_id, create_model=models.ApiKeyScopeAdminCreate(api_key_id=api_key_id, scope_id=scope_id), admin=True))


@api_key_scope_router.delete('/api-keys/{api_key_id}/scopes/{scope_id}/',
                             responses={status.HTTP_404_NOT_FOUND: {
                                 "description": models.ApiKey.not_found_message(), 'model': NotFoundResponse}},
                             status_code=status.HTTP_204_NO_CONTENT,
                             )
async def remove_scope_from_api_key(
    api_key_id: models.ApiKeyTypes.id,
    scope_id: types.ScopeTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())]
):
    async with c.AsyncSession() as session:
        return await models.ApiKeyScope.api_delete(models.ApiKeyScope.DeleteParams.model_construct(session=session, c=c, authorized_user_id=authorization._user_id, id=models.ApiKeyScopeIdBase(api_key_id=api_key_id, scope_id=scope_id)._id))


@api_key_scope_admin_router.delete('/api-keys/{api_key_id}/scopes/{scope_id}/',
                                   responses={status.HTTP_404_NOT_FOUND: {
                                       "description": models.ApiKey.not_found_message(), 'model': NotFoundResponse}},
                                   status_code=status.HTTP_204_NO_CONTENT,
                                   )
async def remove_scope_from_api_key_admin(
    api_key_id: models.ApiKeyTypes.id,
    scope_id: types.ScopeTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))]
):
    async with c.AsyncSession() as session:
        return await models.ApiKeyScope.api_delete(models.ApiKeyScope.DeleteParams.model_construct(
            session=session, c=c, authorized_user_id=authorization._user_id,
            id=models.ApiKeyScopeIdBase(api_key_id=api_key_id, scope_id=scope_id)._id, admin=True))

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
        make_get_auth_dependency(raise_exceptions=False))]
) -> models.GalleryPublic:
    async with c.AsyncSession() as session:
        return models.GalleryPublic.model_validate(await models.Gallery.api_get(models.Gallery.GetParams.model_construct(
            session=session, c=c, authorized_user_id=authorization._user_id, id=gallery_id)))


@gallery_admin_router.get('/{gallery_id}/', responses=models.Gallery.get_responses())
async def get_gallery_by_id_admin(
    gallery_id: models.GalleryTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))]
) -> models.Gallery:
    async with c.AsyncSession() as session:
        return await models.Gallery.api_get(models.Gallery.GetParams.model_construct(
            session=session, c=c, authorized_user_id=authorization._user_id, id=gallery_id, admin=True))


@gallery_router.post('/', responses=models.Gallery.post_responses())
async def post_gallery(
    gallery_create: models.GalleryCreate,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())]
) -> models.GalleryPrivate:
    async with c.AsyncSession() as session:
        return models.GalleryPrivate.model_validate(await models.Gallery.api_post(models.Gallery.PostParams.model_construct(
            session=session, c=c, authorized_user_id=authorization._user_id, create_model=models.GalleryAdminCreate(**gallery_create.model_dump(exclude_unset=True), user_id=authorization._user_id))))


@gallery_admin_router.post('/', responses=models.Gallery.post_responses())
async def post_gallery_admin(
    gallery_create_admin: models.GalleryAdminCreate,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))]
) -> models.Gallery:
    async with c.AsyncSession() as session:
        return await models.Gallery.api_post(models.Gallery.PostParams.model_construct(
            session=session, c=c, authorized_user_id=authorization._user_id, admin=True, create_model=models.GalleryAdminCreate(**gallery_create_admin.model_dump(exclude_unset=True))))


@gallery_router.patch('/{gallery_id}/', responses=models.Gallery.patch_responses())
async def patch_gallery(
    gallery_id: models.GalleryTypes.id,
    gallery_update: models.GalleryUpdate,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())]
) -> models.GalleryPrivate:
    async with c.AsyncSession() as session:
        return models.GalleryPrivate.model_validate(await models.Gallery.api_patch(models.Gallery.PatchParams.model_construct(
            session=session, c=c, authorized_user_id=authorization._user_id, id=gallery_id, update_model=models.GalleryAdminUpdate(**gallery_update.model_dump(exclude_unset=True)))))


@gallery_admin_router.patch('/{gallery_id}/', responses=models.Gallery.patch_responses())
async def patch_gallery_admin(
    gallery_id: models.GalleryTypes.id,
    gallery_update_admin: models.GalleryAdminUpdate,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))]
) -> models.Gallery:
    async with c.AsyncSession() as session:
        return await models.Gallery.api_patch(models.Gallery.PatchParams.model_construct(
            session=session, c=c, authorized_user_id=authorization._user_id, id=gallery_id, admin=True, update_model=models.GalleryAdminUpdate(**gallery_update_admin.model_dump(exclude_unset=True))))


@gallery_router.delete('/{gallery_id}/', responses=models.Gallery.delete_responses(), status_code=status.HTTP_204_NO_CONTENT)
async def delete_gallery(
    gallery_id: models.GalleryTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())]
):
    async with c.AsyncSession() as session:
        return await models.Gallery.api_delete(models.Gallery.DeleteParams.model_construct(session=session, c=c, authorized_user_id=authorization._user_id, id=gallery_id))


@gallery_admin_router.delete('/{gallery_id}/', responses=models.Gallery.delete_responses(), status_code=status.HTTP_204_NO_CONTENT)
async def delete_gallery_admin(
    gallery_id: models.GalleryTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))]
):
    async with c.AsyncSession() as session:
        return await models.Gallery.api_delete(models.Gallery.DeleteParams.model_construct(
            session=session, c=c, authorized_user_id=authorization._user_id, id=gallery_id, admin=True))


@gallery_router.get('/details/available/')
async def get_gallery_available(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())],
    gallery_available: models.GalleryAvailable = Depends(),
):
    async with c.AsyncSession() as session:
        await models.Gallery.api_get_is_available(session, models.GalleryAdminAvailable(
            **gallery_available.model_dump(exclude_unset=True), user_id=authorization._user_id
        ))


@gallery_admin_router.get('/details/available/')
async def get_gallery_available_admin(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))],
    gallery_available_admin: models.GalleryAdminAvailable = Depends(),
):
    async with c.AsyncSession() as session:
        await models.Gallery.api_get_is_available(session, gallery_available_admin)

get_galleries_pagination = get_pagination()


@gallery_router.get('/')
async def get_galleries(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())],
    pagination: models.Pagination = Depends(get_galleries_pagination)

) -> list[models.GalleryPrivate]:

    async with c.AsyncSession() as session:
        galleries = session.exec(select(models.Gallery).where(
            models.Gallery.user_id == authorization._user_id).offset(pagination.offset).limit(pagination.limit)).all()
        return [models.GalleryPrivate.model_validate(gallery) for gallery in galleries]


# need to decide how to deal with gallery permissions and how to return

# @gallery_router.get('/users/{user_id}/', tags=[models.User._ROUTER_TAG])
# async def get_galleries_by_user(
#     user_id: models.UserTypes.id,
#     authorization: typing.Annotated[GetAuthorizationReturn, Depends(
#         get_auth_from_token(raise_exceptions=False))],
#     pagination: PaginationParams = Depends(get_pagination_params),
# ) -> list[models.GalleryPublic]:

#     async with c.AsyncSession() as session:
#         galleries = session.exec(select(models.Gallery).where(
#             models.Gallery.user_id == user_id).offset(pagination.offset).limit(pagination.limit)).all()
#         return [models.GalleryPublic.model_validate(gallery) for gallery in galleries]


@gallery_admin_router.get('/users/{user_id}', tags=[models.User._ROUTER_TAG])
async def get_galleries_by_user_admin(
    user_id: models.UserTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))],
    pagination: models.Pagination = Depends(get_galleries_pagination)
) -> list[models.Gallery]:

    async with c.AsyncSession() as session:
        galleries = session.exec(select(models.Gallery).where(
            models.Gallery.user_id == user_id).offset(pagination.offset).limit(pagination.limit)).all()
        return galleries


class UploadFileToGalleryResponse(BaseModel):
    message: str


@gallery_router.post("/{gallery_id}/upload/", status_code=status.HTTP_201_CREATED)
async def upload_file_to_gallery(
    gallery_id: models.GalleryTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())],
    file: UploadFile
) -> UploadFileToGalleryResponse:

    async with c.AsyncSession() as session:

        gallery = await models.Gallery.read(session, gallery_id)
        if not gallery:
            raise models.Gallery.not_found_exception()

        if gallery.user.id != authorization._user_id:
            gallery_permission = await models.GalleryPermission.api_get(models.GalleryPermission.GetParams.model_construct(session=session, c=c, authorized_user_id=authorization._user_id, id=models.GalleryPermissionIdBase(gallery_id=gallery_id, user_id=authorization._user_id)._id))

            if not gallery_permission:
                if gallery.visibility_level == settings.VISIBILITY_LEVEL_NAME_MAPPING['private']:
                    raise models.Gallery.not_found_exception()

                if gallery.visibility_level == settings.VISIBILITY_LEVEL_NAME_MAPPING['public']:
                    raise HTTPException(status.HTTP_403_FORBIDDEN,
                                        detail='User does not have permission to add files to this gallery')

            if gallery_permission.permission_level < settings.PERMISSION_LEVEL_NAME_MAPPING['editor']:
                raise HTTPException(status.HTTP_403_FORBIDDEN,
                                    detail='User does not have permission to add files to this gallery')

        file_path = (await gallery.get_dir(session, c.galleries_dir)) / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    return UploadFileToGalleryResponse(message="Files uploaded successfully")


@gallery_router.post('/{gallery_id}/sync/')
async def sync_gallery(
    gallery_id: models.GalleryTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())]
) -> DetailOnlyResponse:

    async with c.AsyncSession() as session:
        gallery = await models.Gallery.api_get(models.Gallery.GetParams.model_construct(session=session, c=c, authorized_user_id=authorization._user_id, id=gallery_id))
        dir = await gallery.get_dir(session, c.galleries_dir)
        await gallery.sync_with_local(session, c, dir)
        return DetailOnlyResponse(detail='Synced gallery')

app.include_router(gallery_router)
app.include_router(gallery_admin_router)


# Pages


pages_router = APIRouter(prefix='/pages', tags=['Page'])


class GetProfilePageResponse(GetAuthReturn):
    user: models.UserPrivate | None = None


@pages_router.get('/profile/', tags=[models.User._ROUTER_TAG])
async def get_pages_profile(authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())]) -> GetProfilePageResponse:

    return GetProfilePageResponse(
        **get_auth(authorization).model_dump(),
        user=models.UserPrivate.model_validate(authorization.user)
    )


class GetHomePageResponse(GetAuthReturn):
    pass


@pages_router.get('/home/')
async def get_home_page(authorization: typing.Annotated[GetAuthorizationReturn, Depends(make_get_auth_dependency(raise_exceptions=False))]) -> GetHomePageResponse:
    return GetHomePageResponse(
        **get_auth(authorization).model_dump()
    )


class GetSettingsPageResponse(GetAuthReturn):
    pass


@pages_router.get('/settings/')
async def get_settings_page(
        authorization: typing.Annotated[GetAuthorizationReturn, Depends(
            make_get_auth_dependency(raise_exceptions=False))]
) -> GetSettingsPageResponse:
    return GetSettingsPageResponse(
        **get_auth(authorization).model_dump()
    )


class GetSettingsApiKeysPageResponse(GetAuthReturn):
    api_key_count: int
    api_keys: list[models.ApiKeyPrivate]


@pages_router.get('/settings/api-keys/', tags=[models.ApiKey._ROUTER_TAG])
async def get_settings_api_keys_page(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(make_get_auth_dependency())],
    get_api_keys_query_params: GetApiKeysQueryParamsReturn = Depends(
        get_api_keys_query_params)
) -> GetSettingsApiKeysPageResponse:
    return GetSettingsApiKeysPageResponse(
        **get_auth(authorization).model_dump(),
        api_key_count=await get_user_api_keys_count(authorization),
        api_keys=await get_user_api_keys(authorization, get_api_keys_query_params)
    )


class GetSettingsUserAccessTokensPageResponse(GetAuthReturn):
    user_access_token_count: int
    user_access_tokens: list[models.UserAccessToken]


@pages_router.get('/settings/user-access-tokens/', tags=[models.UserAccessToken._ROUTER_TAG])
async def get_settings_user_access_tokens_page(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(make_get_auth_dependency())],
    pagination: models.Pagination = Depends(user_access_token_pagination)
) -> GetSettingsUserAccessTokensPageResponse:
    return GetSettingsUserAccessTokensPageResponse(
        **get_auth(authorization).model_dump(),
        user_access_token_count=await get_user_access_tokens_count(authorization),
        user_access_tokens=await get_user_access_tokens(authorization, pagination)
    )


class GetStylesPageResponse(GetAuthReturn):
    pass


@pages_router.get('/styles/')
async def get_styles_page(authorization: typing.Annotated[GetAuthorizationReturn, Depends(make_get_auth_dependency(raise_exceptions=False))]) -> GetStylesPageResponse:
    return GetStylesPageResponse(
        **get_auth(authorization).model_dump()
    )


class GetGalleryPageResponse(GetAuthReturn):
    gallery: models.GalleryPublic
    parents: list[models.GalleryPublic]
    children: list[models.GalleryPublic]


@pages_router.get('/galleries/{gallery_id}/', responses={status.HTTP_404_NOT_FOUND: {"description": models.Gallery.not_found_message(), 'model': NotFoundResponse}}, tags=[models.Gallery._ROUTER_TAG])
async def get_gallery_page(
    gallery_id: models.GalleryTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(raise_exceptions=False))],
    root: bool = Query(False),
) -> GetGalleryPageResponse:

    async with c.AsyncSession() as session:
        if root:
            if not authorization.isAuthorized:
                raise models.Gallery.not_found_exception()

            gallery = await models.Gallery.get_root_gallery(session, authorization._user_id)
            gallery_id = gallery._id

        else:
            gallery = await models.Gallery.api_get(models.Gallery.GetParams.model_construct(
                session=session, c=c,  authorized_user_id=authorization._user_id, id=gallery_id
            ))

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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
