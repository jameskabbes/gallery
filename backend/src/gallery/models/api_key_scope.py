
from sqlmodel import Field, Relationship, select, SQLModel
from typing import TYPE_CHECKING, TypedDict, Optional, ClassVar
from gallery import types, utils
from gallery.models.bases.table import Table as BaseTable
from gallery.models import api_key as api_key_module
from pydantic import BaseModel


class ApiKeyScopeId(SQLModel):
    api_key_id: types.ApiKeyScope.api_key_id = Field(
        primary_key=True, index=True, const=True, foreign_key=str(api_key_module.ApiKey.__tablename__) + '.' + api_key_module.ID_COL, ondelete='CASCADE')
    scope_id: types.ApiKeyScope.scope_id = Field(
        primary_key=True, index=True, const=True)


class ApiKeyScopeAdminUpdate(BaseModel):
    pass


class ApiKeyScopeAdminCreate(ApiKeyScopeId):
    pass


class ApiKeyScope(
        BaseTable['ApiKeyScope', ApiKeyScopeId],
        ApiKeyScopeId,
        table=True):

    # __table_args__ = (
    #     PrimaryKeyConstraint('api_key_id', 'scope_id'),
    # )

    api_key: api_key_module.ApiKey = Relationship(
        back_populates='api_key_scopes')

    _ROUTER_TAG: ClassVar[str] = 'Api Key Scope'

    # @classmethod
    # async def create(cls, params):
    #     return ApiKeyScope(
    #         **params.create_model.model_dump(),
    #     )

    # @classmethod
    # async def _check_authorization_new(cls, params):
    #     api_key = await ApiKey.read(params.session, params.create_model.api_key_id)
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
    def _build_get_by_id_query(cls, id: ApiKeyScopeId):
        return select(cls).where(cls.api_key_id == id.api_key_id, cls.scope_id == id.scope_id)
