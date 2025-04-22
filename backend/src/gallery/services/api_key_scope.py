from sqlmodel import Field, Relationship, select, SQLModel
from typing import TYPE_CHECKING, TypedDict, Optional, ClassVar, Annotated, Type

from ..models.tables import ApiKeyScope as ApiKeyScopeTable, ApiKey as ApiKeyTable
from . import base
from .. import types


class ApiKeyScope(base.Service[
    ApiKeyScopeTable,
    types.ApiKeyScope.id,
]):

    _TABLE = ApiKeyScopeTable

    # @classmethod
    # async def _check_authorization_new(cls, params):

    #     api_key = await

    #     api_key = await cls.read(params.session, params.create_model.api_key_id)
    #     if not api_key:
    #         raise ApiKey.not_found_exception()

    #     if not params.admin:
    #         if api_key.user_id != params.authorized_user_id:
    #             raise cls.not_found_exception()

    # @classmethod
    # async def _check_validation_post(cls, params):
    #     if await cls.read(params.session, params.create_model._id):
    #         raise HTTPException(
    #             status_code=status.HTTP_409_CONFLICT, detail='Api key scope already exists')

    # async def _check_authorization_existing(self, params):
    #     if not params.admin:
    #         if self.api_key.user_id != params.authorized_user_id:
    #             raise self.not_found_exception()

    @classmethod
    def table_id(cls, inst: ApiKeyScopeTable):
        return types.ApiKeyScopeId(
            api_key_id=inst.api_key_id,
            scope_id=inst.scope_id,
        )

    @classmethod
    def _build_select_by_id(cls, id):
        return select(cls._TABLE).where(cls._TABLE.api_key_id == id.api_key_id, cls._TABLE.scope_id == id.scope_id)
