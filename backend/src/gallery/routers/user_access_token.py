from fastapi import Depends, status
from sqlmodel import select, func
from ..models.tables import UserAccessToken as UserAccessTokenTable
from ..services.user_access_token import UserAccessToken as UserAccessTokenService
from ..schemas import user_access_token as user_access_token_schema, pagination as pagination_schema, api as api_schema
from ..routers import user as user_router
from . import base
from .. import types
from typing import Annotated, cast, Literal
from ..auth import utils as auth_utils


def user_access_token_pagination(
    pagination: Annotated[pagination_schema.Pagination, Depends(
        base.get_pagination(default_limit=50, max_limit=500))]
):
    return pagination


class _Base(
    base.Router[
        UserAccessTokenTable,
        types.UserAccessToken.id,
        user_access_token_schema.UserAccessTokenAdminCreate,
        user_access_token_schema.UserAccessTokenAdminUpdate,
        str
    ]
):

    _PREFIX = '/user_access_tokens'
    _TAG = 'User Access Token'
    _SERVICE = UserAccessTokenService


class UserAccessTokenRouter(_Base):

    _ADMIN = False

    def _set_routes(self):

        @self.router.get('/', tags=[user_router._Base._TAG])
        async def get_user_access_tokens(
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(c=self.client))],
            pagination: pagination_schema.Pagination = Depends(
                user_access_token_pagination)

        ) -> list[UserAccessTokenTable]:

            return list(await self.get_many({
                'authorization': authorization,
                'c': self.client,
                'pagination': pagination,
            }))

        @self.router.get('/{user_access_token_id}/')
        async def get_user_access_token_by_id(
            user_access_token_id: types.UserAccessToken.id,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(c=self.client))]
        ) -> UserAccessTokenTable:

            return await self.get({
                'authorization': authorization,
                'c': self.client,
                'id': user_access_token_id,
            })

        @self.router.delete('/{user_access_token_id}/', status_code=status.HTTP_204_NO_CONTENT)
        async def delete_user_access_token(
            user_access_token_id: types.UserAccessToken.id,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(c=self.client))]
        ):
            return await self.delete({
                'authorization': authorization,
                'c': self.client,
                'id': user_access_token_id,
            })

        @self.router.get('/details/count/')
        async def get_user_access_tokens_count(
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(c=self.client))],
        ) -> int:
            async with self.client.AsyncSession() as session:
                query = select(func.count()).select_from(UserAccessTokenTable).where(
                    UserAccessTokenTable.user_id == authorization._user_id)
                return (await session.exec(query)).one()


class UserAccessTokenAdminRouter(_Base):

    _ADMIN = True

    def _set_routes(self):

        @self.router.get('/users/{user_id}/', tags=[user_router._Base._TAG])
        async def get_user_access_tokens_admin(
            user_id: types.User.id,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(required_scopes={'admin'}, c=self.client))],
            pagination: pagination_schema.Pagination = Depends(
                user_access_token_pagination)
        ) -> list[UserAccessTokenTable]:

            return list(await self.get_many({
                'authorization': authorization,
                'c': self.client,
                'pagination': pagination,
                'query': select(UserAccessTokenTable).where(
                    UserAccessTokenTable.user_id == user_id)

            }))

        @self.router.get('/{user_access_token_id}/')
        async def get_user_access_token_by_id_admin(
            user_access_token_id: types.UserAccessToken.id,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(required_scopes={'admin'}, c=self.client))]
        ) -> UserAccessTokenTable:

            return await self.get({
                'authorization': authorization,
                'c': self.client,
                'id': user_access_token_id,
            })

        @self.router.post('/')
        async def post_user_access_token_admin(
            user_access_token_create_admin: user_access_token_schema.UserAccessTokenAdminCreate,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(required_scopes={'admin'}, c=self.client))]
        ) -> UserAccessTokenTable:

            return await self.post({
                'authorization': authorization,
                'c': self.client,
                'create_model': user_access_token_create_admin,
            })

        @self.router.delete('/{user_access_token_id}/', status_code=status.HTTP_204_NO_CONTENT)
        async def delete_user_access_token_admin(
            user_access_token_id: types.UserAccessToken.id,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(required_scopes={'admin'}, c=self.client))]
        ):

            return await self.delete({
                'authorization': authorization,
                'c': self.client,
                'id': user_access_token_id,
            })
