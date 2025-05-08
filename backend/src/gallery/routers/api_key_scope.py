from .. import types
from . import base
from ..models.tables import ApiKeyScope as ApiKeyScopeTable
from ..services.api_key_scope import ApiKeyScope as ApiKeyScopeService
from ..schemas import api_key_scope as api_key_scope_schema
from typing import Annotated
from ..auth import utils as auth_utils
from fastapi import Depends, status


class _Base(
    base.Router[
        ApiKeyScopeTable,
        types.ApiKeyScope.id,
        api_key_scope_schema.ApiKeyScopeAdminCreate,
        api_key_scope_schema.ApiKeyScopeAdminUpdate,
    ],
):
    _PREFIX = '/api_key_scopes'
    _TAGS = ['Api Key Scope']
    _SERVICE = ApiKeyScopeService


class ApiKeyScopeRouter(_Base):

    _ADMIN = False

    def _set_routes(self):

        @self.router.post('/{api_key_id}/{scope_id}/')
        async def add_scope_to_api_key(
            api_key_id: types.ApiKey.id,
            scope_id: types.Scope.id,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(c=self.client))]
        ) -> None:
            api_key_scope = await self.post({
                'authorization': authorization,
                'c': self.client,
                'create_model': api_key_scope_schema.ApiKeyScopeAdminCreate(
                    api_key_id=api_key_id, scope_id=scope_id),
            })

        @self.router.delete('/{api_key_id}/{scope_id}/', status_code=status.HTTP_204_NO_CONTENT)
        async def remove_scope_from_api_key(
            api_key_id: types.ApiKey.id,
            scope_id: types.Scope.id,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(c=self.client))]
        ) -> None:
            await self.delete({
                'authorization': authorization,
                'c': self.client,
                'id': types.ApiKeyScope.id(
                    api_key_id=api_key_id, scope_id=scope_id),
            })


class ApiKeyScopeAdminRouter(_Base):

    _ADMIN = True

    def _set_routes(self):

        @self.router.post('/{api_key_id}/{scope_id}/')
        async def add_scope_to_api_key(
            api_key_id: types.ApiKey.id,
            scope_id: types.Scope.id,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(c=self.client, required_scopes={'admin'}))]
        ) -> None:
            api_key_scope = await self.post({
                'authorization': authorization,
                'c': self.client,
                'create_model': api_key_scope_schema.ApiKeyScopeAdminCreate(
                    api_key_id=api_key_id, scope_id=scope_id),
            })

        @self.router.delete('/{api_key_id}/{scope_id}/', status_code=status.HTTP_204_NO_CONTENT)
        async def remove_scope_from_api_key(
            api_key_id: types.ApiKey.id,
            scope_id: types.Scope.id,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(c=self.client, required_scopes={'admin'}))]
        ) -> None:
            await self.delete({
                'authorization': authorization,
                'c': self.client,
                'id': types.ApiKeyScope.id(
                    api_key_id=api_key_id, scope_id=scope_id),
            })
