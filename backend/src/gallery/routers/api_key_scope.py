from fastapi import Depends, status
from typing import Annotated

from src.gallery import types
from src.gallery.routers import base
from src.gallery.models.tables import ApiKeyScope as ApiKeyScopeTable
from src.gallery.services.api_key_scope import ApiKeyScope as ApiKeyScopeService
from src.gallery.schemas import api_key_scope as api_key_scope_schema
from src.gallery.auth import utils as auth_utils


class _Base(
    base.Router[
        ApiKeyScopeTable,
        types.ApiKeyScope.id,
        api_key_scope_schema.ApiKeyScopeAdminCreate,
        api_key_scope_schema.ApiKeyScopeAdminUpdate,
    ],
):
    _PREFIX = '/api_key_scopes'
    _TAG = 'API Key Scope'
    _SERVICE = ApiKeyScopeService


class ApiKeyScopeRouter(_Base):

    _ADMIN = False

    def _set_routes(self):

        @self.router.post('/{api_key_id}/{scope_id}/')
        async def add_scope_to_api_key(
            api_key_id: types.ApiKey.id,
            scope_id: types.Scope.id,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency())]
        ) -> None:
            api_key_scope = await self.post({
                'authorization': authorization,
                'create_model': api_key_scope_schema.ApiKeyScopeAdminCreate(
                    api_key_id=api_key_id, scope_id=scope_id),
            })

        @self.router.delete('/{api_key_id}/{scope_id}/', status_code=status.HTTP_204_NO_CONTENT)
        async def remove_scope_from_api_key(
            api_key_id: types.ApiKey.id,
            scope_id: types.Scope.id,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency())]
        ) -> None:
            await self.delete({
                'authorization': authorization,
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
                auth_utils.make_get_auth_dependency(required_scopes={'admin'}))]
        ) -> None:
            api_key_scope = await self.post({
                'authorization': authorization,
                'create_model': api_key_scope_schema.ApiKeyScopeAdminCreate(
                    api_key_id=api_key_id, scope_id=scope_id),
            })

        @self.router.delete('/{api_key_id}/{scope_id}/', status_code=status.HTTP_204_NO_CONTENT)
        async def remove_scope_from_api_key(
            api_key_id: types.ApiKey.id,
            scope_id: types.Scope.id,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(required_scopes={'admin'}))]
        ) -> None:
            await self.delete({
                'authorization': authorization,
                'id': types.ApiKeyScope.id(
                    api_key_id=api_key_id, scope_id=scope_id),
            })
