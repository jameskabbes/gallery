from fastapi import Depends, status
from sqlmodel import select, func
from pydantic import BaseModel
from ..models.tables import ApiKey as ApiKeyTable
from ..services.api_key import ApiKey as ApiKeyService
from ..schemas import api_key as api_key_schema, pagination as pagination_schema, api as api_schema, order_by as order_by_schema
from . import base
from .. import types
from typing import Annotated, cast
from ..auth import utils as auth_utils

from collections.abc import Sequence


class _Base(
    base.Router[
        ApiKeyTable,
        types.User.id,
        api_key_schema.ApiKeyAdminCreate,
        api_key_schema.ApiKeyAdminUpdate,
        types.ApiKey.order_by,
    ],
):
    _PREFIX = '/api_keys'
    _TAGS = ['API Key']
    _SERVICE = ApiKeyService

    def __init__(self, *args, **kwargs):
        self.order_by_depends = self.make_order_by_dependency()
        super().__init__(*args, **kwargs)


api_key_pagination = base.get_pagination()


class ApiKeyJWTResponse(BaseModel):
    jwt: types.JwtEncodedStr


class ApiKeyRouter(_Base):

    _ADMIN = False

    def _set_routes(self):

        @self.router.get('/{api_key_id}/')
        async def get_api_key_by_id(
            api_key_id: types.ApiKey.id,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(c=self.client, ))]
        ) -> api_key_schema.ApiKeyPrivate:

            return api_key_schema.ApiKeyPrivate.model_validate(
                await self.get({
                    'authorization': authorization,
                    'c': self.client,
                    'id': api_key_id,
                })
            )

        @self.router.get('/')
        async def get_user_api_keys(
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(c=self.client))],
            pagination: Annotated[pagination_schema.Pagination, Depends(api_key_pagination)],
            order_bys: Annotated[list[order_by_schema.OrderBy[types.ApiKey.order_by]], Depends(
                self.order_by_depends)]
        ) -> list[api_key_schema.ApiKeyPrivate]:

            return [api_key_schema.ApiKeyPrivate.model_validate(api_key) for api_key in await self.get_many({
                'authorization': authorization,
                'c': self.client,
                'order_bys': order_bys,
                'pagination': pagination,
                'query': select(ApiKeyTable).where(ApiKeyTable.user_id == authorization._user_id)
            })]

        @self.router.post('/')
        async def post_api_key_to_user(
            api_key_create: api_key_schema.ApiKeyCreate,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(c=self.client))]
        ) -> api_key_schema.ApiKeyPrivate:

            return api_key_schema.ApiKeyPrivate.model_validate(
                await self.post({
                    'authorization': authorization,
                    'c': self.client,
                    'create_model': api_key_schema.ApiKeyAdminCreate(
                        **api_key_create.model_dump(
                            exclude_unset=True),
                        user_id=cast(types.User.id, authorization._user_id)
                    )
                })
            )

        @self.router.patch('/{api_key_id}/')
        async def patch_api_key(
            api_key_id: types.ApiKey.id,
            api_key_update: api_key_schema.ApiKeyUpdate,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(c=self.client,))]
        ) -> api_key_schema.ApiKeyPrivate:

            return api_key_schema.ApiKeyPrivate.model_validate(
                await self.patch({
                    'authorization': authorization,
                    'c': self.client,
                    'id': api_key_id,
                    'update_model': api_key_schema.ApiKeyAdminUpdate(
                        **api_key_update.model_dump(exclude_unset=True))
                })
            )

        @self.router.delete('/{api_key_id}/', status_code=status.HTTP_204_NO_CONTENT)
        async def delete_api_key(
            api_key_id: types.ApiKey.id,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(c=self.client))]
        ):

            return await self.delete({
                'authorization': authorization,
                'c': self.client,
                'id': api_key_id,
            })

        @self.router.get('/{api_key_id}/generate-jwt/')
        async def get_api_key_jwt(
            api_key_id: types.ApiKey.id,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(c=self.client))]
        ) -> ApiKeyJWTResponse:

            async with self.client.AsyncSession() as session:
                api_key = await self.get({
                    'authorization': authorization,
                    'c': self.client,
                    'id': api_key_id,
                })

                return ApiKeyJWTResponse(
                    jwt=self.client.jwt_encode(cast(dict, ApiKeyService.to_jwt_payload(api_key))))

        @self.router.get('/details/available/')
        async def get_api_key_available(
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(c=self.client,))],
            api_key_available: api_key_schema.ApiKeyAvailable = Depends(),
        ) -> api_schema.IsAvailableResponse:
            async with self.client.AsyncSession() as session:

                return api_schema.IsAvailableResponse(
                    available=await ApiKeyService.is_available(
                        session, api_key_schema.ApiKeyAdminAvailable(
                            **api_key_available.model_dump(exclude_unset=True),
                            user_id=cast(types.User.id, authorization._user_id)
                        )
                    )
                )

        @self.router.get('/details/count/')
        async def get_user_api_keys_count(
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(c=self.client,))],
        ) -> int:
            async with self.client.AsyncSession() as session:
                query = select(func.count()).select_from(ApiKeyTable).where(
                    ApiKeyTable.user_id == authorization._user_id)
                return (await session.exec(query)).one()


class ApiKeyAdminRouter(_Base):

    _ADMIN = False

    def _set_routes(self):

        @self.router.get('/{api_key_id}/')
        async def get_api_key_by_id_admin(
            api_key_id: types.ApiKey.id,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(c=self.client, required_scopes={'admin'}))]
        ) -> ApiKeyTable:

            return await self.get({
                'authorization': authorization,
                'c': self.client,
                'id': api_key_id,
            })

        @self.router.post('/')
        async def post_api_key_to_user_admin(
            api_key_create_admin: api_key_schema.ApiKeyAdminCreate,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(c=self.client, required_scopes={'admin'}))]
        ) -> ApiKeyTable:

            return await self.post({
                'authorization': authorization,
                'c': self.client,
                'create_model': api_key_create_admin
            })

        @self.router.patch('/{api_key_id}/')
        async def patch_api_key_admin(
            api_key_id: types.ApiKey.id,
            api_key_update_admin: api_key_schema.ApiKeyAdminUpdate,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(c=self.client, required_scopes={'admin'}))]
        ) -> ApiKeyTable:

            return await self.patch({
                'authorization': authorization,
                'c': self.client,
                'id': api_key_id,
                'update_model': api_key_update_admin
            })

        @self.router.delete('/{api_key_id}/', status_code=status.HTTP_204_NO_CONTENT)
        async def delete_api_key_admin(
            api_key_id: types.ApiKey.id,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(c=self.client, required_scopes={'admin'}))]
        ):

            return await self.delete({
                'authorization': authorization,
                'c': self.client,
                'id': api_key_id,
            })

        # Add User tag to this

        # @self.router.get('/')
        # async def get_user_api_keys(
        #     authorization: Annotated[auth_utils.GetAuthReturn, Depends(
        #         auth_utils.make_get_auth_dependency(c=self.client))],
        #     pagination: Annotated[pagination_schema.Pagination, Depends(api_key_pagination)],
        #     order_bys: Annotated[list[order_by_schema.OrderBy[types.ApiKey.order_by]], Depends(
        #         self.order_by_depends)]
        # ) -> list[api_key_schema.ApiKeyPrivate]:

        #     return [ApiKeyService.to_api_key_private(api_key) for api_key in await self.get_many({
        #         'authorization': authorization,
        #         'c': self.client,
        #         'order_bys': order_bys,
        #         'pagination': pagination,
        #         'query': select(ApiKeyTable).options(selectinload(ApiKeyTable.api_key_scopes)).where(
        #             ApiKeyTable.user_id == authorization._user_id)
        #     })
        #     ]

        @self.router.get('/users/{user_id}/')
        async def get_user_api_keys_admin(
            user_id: types.User.id,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(c=self.client, required_scopes={'admin'}))],
            pagination: Annotated[pagination_schema.Pagination, Depends(api_key_pagination)],
            order_bys: Annotated[list[order_by_schema.OrderBy[types.ApiKey.order_by]], Depends(
                self.order_by_depends)]

        ) -> list[ApiKeyTable]:

            return list(await self.get_many(
                {
                    'authorization': authorization,
                    'c': self.client,
                    'order_bys': order_bys,
                    'pagination': pagination,
                    'query': select(ApiKeyTable).where(ApiKeyTable.user_id == authorization._user_id)}))

        @self.router.get('/details/available/')
        async def get_api_key_available_admin(
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(c=self.client, required_scopes={'admin'}))],
            api_key_available_admin: api_key_schema.ApiKeyAdminAvailable = Depends(),
        ):

            async with self.client.AsyncSession() as session:
                return api_schema.IsAvailableResponse(
                    available=await ApiKeyService.is_available(
                        session, api_key_available_admin
                    )
                )
