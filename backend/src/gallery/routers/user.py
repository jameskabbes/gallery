from fastapi import Depends, status
from sqlmodel import select
from ..models.tables import User as UserTable
from ..services.user import User as UserService
from ..schemas import user as user_schema, pagination as pagination_schema, api as api_schema
from . import base
from .. import types
from typing import Annotated, cast, Type
from ..auth import utils as auth_utils
from ..services import base as base_service


class UserRouter(
        base.Router[
            UserTable,
            types.User.id,
        ]):

    _ADMIN = False
    _SERVICE = base.base_service.ServiceProtocol[
        UserTable,
        types.User.id,
    ]

    def _set_routes(self):

        @self.router.get('/me/')
        async def get_user_me(
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(raise_exceptions=True, c=self.client))]
        ) -> user_schema.UserPrivate:
            user = self.get(self.client, authorization, cast(
                types.User.id, authorization._user_id))
            return user_schema.UserPrivate.model_validate(user)

        @self.router.patch('/me/')
        async def patch_user_me(
            user_update: user_schema.UserUpdate,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(raise_exceptions=True, c=self.client))]
        ) -> user_schema.UserPrivate:
            async with self.client.AsyncSession() as session:
                user = await UserService.update({
                    'session': session,
                    'c': self.client,
                    'id': cast(types.User.id, authorization._user_id),
                    'authorized_user_id': authorization._user_id,
                    'update_model': user_update,
                    'admin': False,
                })
                return user_schema.UserPrivate.model_validate(user)

        @self.router.delete('/me/', status_code=status.HTTP_204_NO_CONTENT)
        async def delete_user_me(
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(raise_exceptions=True, c=self.client))]
        ):
            async with self.client.AsyncSession() as session:
                return await UserService.delete({
                    'session': session,
                    'c': self.client,
                    'id': cast(types.User.id, authorization._user_id),
                    'authorized_user_id': authorization._user_id,
                    'admin': False,
                })

        @self.router.get('/{user_id}/')
        async def get_user_by_id(
            user_id: types.User.id,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(raise_exceptions=False, c=self.client))]
        ) -> user_schema.UserPublic:
            async with self.client.AsyncSession() as session:
                return user_schema.UserPublic.model_validate(await UserService.read({
                    'session': session,
                    'c': self.client,
                    'id': user_id,
                    'authorized_user_id': authorization._user_id,
                    'admin': False,
                }))

        @self.router.get('/')
        async def get_users(
            pagination: Annotated[pagination_schema.Pagination, Depends(
                base.get_pagination())]
        ) -> list[user_schema.UserPublic]:

            async with self.client.AsyncSession() as session:
                query = select(UserTable).where(
                    UserTable.username != None)
                query = UserService.build_pagination(query, pagination)
                users = (await session.exec(query)).all()
                return [user_schema.UserPublic.model_validate(user) for user in users]

        @self.router.get('/available/username/{username}/',
                         responses={status.HTTP_409_CONFLICT: {
                             "description": 'Username already exists', 'model': api_schema.IsAvailableResponse}})
        async def get_user_username_available(username: types.User.username):
            async with self.client.AsyncSession() as session:
                return api_schema.IsAvailableResponse(
                    available=not await UserService.is_username_available(session, username))


# class UserAdminRouter(_Base, base.Router[UserTable, types.User.id, UserService, user_schema.UserCreate, user_schema.UserUpdate]):

#     _ADMIN = True
#     _PREFIX = PREFIX
#     _TAGS = [TAG]

#     def _set_routes(self):

#         @self.router.get('/{user_id}/')
#         async def get_user_by_id(
#             user_id: types.User.id,
#             authorization: Annotated[auth_utils.GetAuthReturn, Depends(
#                 auth_utils.make_get_auth_dependency(required_scopes={'admin'}, c=self.client))]
#         ) -> UserTable:
#             async with self.client.AsyncSession() as session:
#                 return await UserService.read({
#                     'admin': True,
#                     'c': self.client,
#                     'session': session,
#                     'id': user_id,
#                     'authorized_user_id': authorization._user_id,
#                 })

#         @self.router.get('/')
#         async def get_users_admin(
#             authorization: Annotated[auth_utils.GetAuthReturn, Depends(
#                 auth_utils.make_get_auth_dependency(required_scopes={'admin'}, c=self.client))],
#             pagination: Annotated[pagination_schema.Pagination, Depends(
#                 base.get_pagination())]
#         ) -> list[UserTable]:

#             async with self.client.AsyncSession() as session:
#                 query = select(UserTable)
#                 query = UserService.build_pagination(query, pagination)
#                 users = (await session.exec(query)).all()
#                 return list(users)

#         @self.router.post('/')
#         async def post_user(
#             user_create_admin: user_schema.UserAdminCreate,
#             authorization: Annotated[auth_utils.GetAuthReturn, Depends(
#                 auth_utils.make_get_auth_dependency(required_scopes={'admin'}, c=self.client))]
#         ) -> UserTable:
#             async with self.client.AsyncSession() as session:
#                 return await UserService.create({
#                     'session': session,
#                     'admin': True,
#                     'authorized_user_id': authorization._user_id,
#                     'c': self.client,
#                     'create_model': user_create_admin,
#                 })

#         @self.router.patch('/{user_id}/')
#         async def patch_user(
#             user_id: types.User.id,
#             user_update_admin: user_schema.UserAdminUpdate,
#             authorization: Annotated[auth_utils.GetAuthReturn, Depends(
#                 auth_utils.make_get_auth_dependency(required_scopes={'admin'}, c=self.client))]
#         ) -> UserTable:
#             async with self.client.AsyncSession() as session:
#                 return await UserService.update({
#                     'session': session,
#                     'c': self.client,
#                     'admin': True,
#                     'authorized_user_id': authorization._user_id,
#                     'id': user_id,
#                     'update_model': user_update_admin,
#                 })

#         @self.router.delete('/{user_id}/', status_code=status.HTTP_204_NO_CONTENT)
#         async def delete_user(
#             user_id: types.User.id,
#             authorization: Annotated[auth_utils.GetAuthReturn, Depends(
#                 auth_utils.make_get_auth_dependency(required_scopes={'admin'}, c=self.client))]
#         ):
#             async with self.client.AsyncSession() as session:
#                 return await UserService.delete({
#                     'session': session,
#                     'c': self.client,
#                     'authorized_user_id': authorization._user_id,
#                     'id': user_id,
#                     'admin': True,
#                 })
