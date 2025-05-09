from fastapi import Depends, status
from sqlmodel import select
from ..models.tables import UserAccessToken as UserAccessTokenTable
from ..services.user_access_token import UserAccessToken as UserAccessTokenService
from ..schemas import user_access_token as user_access_token_schema, pagination as pagination_schema, api as api_schema
from . import base
from .. import types
from typing import Annotated, cast
from ..auth import utils as auth_utils


WrongUserPermissionUserAccessToken = HTTPException(
    status.HTTP_403_FORBIDDEN, detail='User does not have permission to view another user\'s access tokens')


def user_access_token_pagination(
    pagination: Annotated[pagination_schema.Pagination, Depends(
        base.get_pagination(default_limit=50, max_limit=500))]
):
    return pagination


class _Base(base.Router[UserAccessTokenTable, types.UserAccessToken.id, user_access_token_schema.UserAccessTokenAdminCreate, user_access_token_schema.UserAccessTokenAdminUpdate]):

    _PREFIX = '/user_access_tokens'
    _TAGS = ['User Access Token']
    _SERVICE = UserAccessTokenService


class UserAccessTokenRouter(_Base):

    _ADMIN = False

    def _set_routes(self):
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

        # need to add User tag to this

#         @self.router.get('/')
#         async def get_user_access_tokens(
#             authorization: Annotated[auth_utils.GetAuthReturn, Depends(
#                 auth_utils.make_get_auth_dependency(c=self.client))],
#             pagination: pagination_schema.Pagination = Depends(
#                 user_access_token_pagination)

#         ) -> list[UserAccessTokenTable]:

#             return await self.get_many({
#                 'authorization': authorization,
#                 'c': self.client,
#                 'pagination': pagination,
#             })

#             async with self.client.AsyncSession() as session:
#                 query = select(UserAccessTokenTable).where(
#                     UserAccessTokenTable.user_id == authorization._user_id)
#                 query = tables.build_pagination(query, pagination)
#                 user_access_tokens = session.exec(query).all()
#                 return user_access_tokens

#         @self.router.get('/details/count/')
#         async def get_user_access_tokens_count(
#             authorization: Annotated[auth_utils.GetAuthReturn, Depends(
#                 auth_utils.make_get_auth_dependency())],
#         ) -> int:
#             async with self.client.AsyncSession() as session:
#                 query = select(func.count()).select_from(UserAccessTokenTable).where(
#                     UserAccessTokenTable.user_id == authorization._user_id)
#                 return session.exec(query).one()


# class UserAccessTokenAdminRouter(base.Router[UserAccessTokenTable]):

#     _ADMIN = True
#     _PREFIX = PREFIX
#     _TAGS = [TAG]

#     def _set_routes(self):

#         @self.router.get('/{user_access_token_id}/', responses=UserAccessTokenTable.get_responses())
#         async def get_user_access_token_by_id_admin(
#             user_access_token_id: types.UserAccessToken.id,
#             authorization: Annotated[auth_utils.GetAuthReturn, Depends(
#                 auth_utils.make_get_auth_dependency(required_scopes={'admin'}))]
#         ) -> UserAccessTokenTable:
#             async with self.client.AsyncSession() as session:
#                 return await UserAccessTokenTable.api_get(UserAccessTokenTable.GetParams.model_construct(
#                     session=session, c=self.client, authorized_user_id=authorization._user_id, id=user_access_token_id, admin=True))

#         @self.router.post('/', responses=UserAccessTokenTable.post_responses())
#         async def post_user_access_token_admin(
#             user_access_token_create_admin: UserAccessTokenTableAdminCreate,
#             authorization: Annotated[auth_utils.GetAuthReturn, Depends(
#                 auth_utils.make_get_auth_dependency(required_scopes={'admin'}))]
#         ) -> UserAccessTokenTable:
#             async with self.client.AsyncSession() as session:
#                 return await UserAccessTokenTable.api_post(UserAccessTokenTable.PostParams.model_construct(
#                     session=session, c=self.client, authorized_user_id=authorization._user_id, admin=True, create_model=user_access_token_create_admin))

#         @self.router.delete('/{user_access_token_id}/', responses=UserAccessTokenTable.delete_responses(), status_code=status.HTTP_204_NO_CONTENT)
#         async def delete_user_access_token_admin(
#             user_access_token_id: types.UserAccessToken.id,
#             authorization: Annotated[auth_utils.GetAuthReturn, Depends(
#                 auth_utils.make_get_auth_dependency(required_scopes={'admin'}))]
#         ):
#             async with self.client.AsyncSession() as session:
#                 return await UserAccessTokenTable.api_delete(UserAccessTokenTable.DeleteParams.model_construct(
#                     session=session, c=self.client, authorized_user_id=authorization._user_id, id=user_access_token_id, admin=True))

#         @self.router.get('/users/{user_id}/', tags=[tables.User._ROUTER_TAG], responses={status.HTTP_404_NOT_FOUND: {"description": tables.User.not_found_message(), 'model': NotFoundResponse}})
#         async def get_user_access_tokens_admin(
#             user_id: tables.UserTypes.id,
#             authorization: Annotated[auth_utils.GetAuthReturn, Depends(
#                 auth_utils.make_get_auth_dependency(required_scopes={'admin'}))],
#             pagination: tables.Pagination = Depends(
#                 user_access_token_pagination)
#         ) -> list[UserAccessTokenTable]:
#             async with self.client.AsyncSession() as session:

#                 query = select(UserAccessTokenTable).where(
#                     UserAccessTokenTable.user_id == user_id)
#                 query = tables.build_pagination(query, pagination)
#                 user_access_tokens = session.exec(query).all()
#                 return user_access_tokens
