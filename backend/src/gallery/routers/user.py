from fastapi import Depends, status
from sqlmodel import select
from ..models.tables import User as UserTable
from ..services.user import User as UserService
from ..schemas import user as user_schema, pagination as pagination_schema, api as api_schema
from . import base
from .. import types
from typing import Annotated, cast
from ..auth import utils as auth_utils

from collections.abc import Sequence


class _Base(
    base.Router[
        UserTable,
        types.User.id,
        user_schema.UserAdminCreate,
        user_schema.UserAdminUpdate,
    ],
):
    _PREFIX = '/users'
    _TAG = 'User'
    _SERVICE = UserService


class UserRouter(_Base):

    _ADMIN = False

    def _set_routes(self):

        @self.router.get('/')
        async def get_users(
            pagination: Annotated[pagination_schema.Pagination, Depends(
                base.get_pagination())],
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(raise_exceptions=False, c=self.client))]
        ) -> Sequence[user_schema.UserPublic]:

            return [user_schema.UserPublic.model_validate(user) for user in await self.get_many({
                'authorization': authorization,
                'c': self.client,
                'pagination': pagination,
            })]

        @self.router.get('/me/')
        async def get_user_me(
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(raise_exceptions=True, c=self.client))]
        ) -> user_schema.UserPrivate:
            user = await self.get({'authorization': authorization, 'c': self.client, 'id': cast(
                types.User.id, authorization._user_id)})
            return user_schema.UserPrivate.model_validate(user)

        @self.router.patch('/me/')
        async def patch_user_me(
            user_update: user_schema.UserUpdate,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(raise_exceptions=True, c=self.client))]
        ) -> user_schema.UserPrivate:
            user = await self.patch({
                'authorization': authorization,
                'c': self.client,
                'id': cast(types.User.id, authorization._user_id),
                'update_model': user_schema.UserAdminUpdate.model_validate(user_update),
            })
            return user_schema.UserPrivate.model_validate(user)

        @self.router.delete('/me/', status_code=status.HTTP_204_NO_CONTENT)
        async def delete_user_me(
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(raise_exceptions=True, c=self.client))]
        ):
            await self.delete({
                'authorization': authorization,
                'c': self.client,
                'id': cast(types.User.id, authorization._user_id),
            })

        @self.router.get('/{user_id}/')
        async def get_user_by_id(
            user_id: types.User.id,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(raise_exceptions=False, c=self.client))]
        ) -> user_schema.UserPublic:
            user = await self.get({
                'authorization': authorization,
                'c': self.client,
                'id': user_id,
            })
            return user_schema.UserPublic.model_validate(user)

        @self.router.get('/available/username/{username}/',
                         responses={status.HTTP_409_CONFLICT: {
                             "description": 'Username already exists', 'model': api_schema.IsAvailableResponse}})
        async def get_user_username_available(username: types.User.username):
            async with self.client.AsyncSession() as session:
                return api_schema.IsAvailableResponse(
                    available=not await UserService.is_username_available(session, username))


class UserAdminRouter(_Base):

    _ADMIN = True

    def _set_routes(self):
        @self.router.get('/')
        async def get_users_admin(
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(required_scopes={'admin'}, c=self.client))],
            pagination: Annotated[pagination_schema.Pagination, Depends(
                base.get_pagination())]
        ) -> list[user_schema.UserPrivate]:

            return [
                user_schema.UserPrivate.model_validate(user) for user in await self.get_many({
                    'authorization': authorization,
                    'c': self.client,
                    'pagination': pagination,
                })]

        @self.router.get('/{user_id}/')
        async def get_user_by_id(
            user_id: types.User.id,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(required_scopes={'admin'}, c=self.client))]
        ) -> user_schema.UserPrivate:
            return user_schema.UserPrivate.model_validate(
                await self.get({
                    'authorization': authorization,
                    'c': self.client,
                    'id': user_id,
                })
            )

        @self.router.post('/')
        async def post_user(
            user_create_admin: user_schema.UserAdminCreate,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(required_scopes={'admin'}, c=self.client))]
        ) -> user_schema.UserPrivate:

            return user_schema.UserPrivate.model_validate(await self.post({
                'authorization': authorization,
                'c': self.client,
                'create_model': user_create_admin,
            })
            )

        @self.router.patch('/{user_id}/')
        async def patch_user(
            user_id: types.User.id,
            user_update_admin: user_schema.UserAdminUpdate,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(required_scopes={'admin'}, c=self.client))]
        ) -> user_schema.UserPrivate:
            return user_schema.UserPrivate.model_validate(await self.patch({
                'authorization': authorization,
                'c': self.client,
                'id': user_id,
                'update_model': user_update_admin,
            }))

        @self.router.delete('/{user_id}/', status_code=status.HTTP_204_NO_CONTENT)
        async def delete_user(
            user_id: types.User.id,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(required_scopes={'admin'}, c=self.client))]
        ):
            return await self.delete({
                'authorization': authorization,
                'c': self.client,
                'id': user_id,
            })
