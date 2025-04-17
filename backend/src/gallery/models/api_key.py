from sqlmodel import Field, Relationship, select, SQLModel
from sqlalchemy import Column
from typing import TYPE_CHECKING, TypedDict, Optional, Self
from pydantic import BaseModel

from .. import types, utils
from .bases.table import Table as BaseTable
from .bases import auth_credential
from .custom_field_types import timestamp
from .user import User


ID_COL = 'id'

if TYPE_CHECKING:
    from .api_key_scope import ApiKeyScope


class ApiKeyAvailable(BaseModel):
    name: types.ApiKey.name


class ApiKeyAdminAvailable(ApiKeyAvailable):
    user_id: types.User.id


class ApiKeyImport(auth_credential.Import):
    pass


class ApiKeyUpdate(ApiKeyImport, auth_credential.Update):
    name: Optional[types.ApiKey.name] = None


class ApiKeyAdminUpdate(ApiKeyUpdate):
    pass


class ApiKeyCreate(ApiKeyImport, auth_credential.Create):
    name: types.ApiKey.name


class ApiKeyAdminCreate(ApiKeyCreate):
    user_id: types.User.id


class JwtPayload(auth_credential.JwtPayload):
    sub: types.User.id


class JwtModel(auth_credential.JwtModel):
    id: types.User.id


class ApiKey(
        BaseTable[types.ApiKey.id, ApiKeyAdminCreate, ApiKeyAdminUpdate],
        auth_credential.Table,
        auth_credential.JwtIO[JwtPayload, JwtModel],
        table=True):

    __tablename__ = 'api_key'  # type: ignore

    auth_type = 'api_key'
    _ROUTER_TAG = 'Api Key'

    id: types.ApiKey.id = Field(
        primary_key=True, index=True, unique=True, const=True)
    issued: types.AuthCredential.issued = Field(
        const=True, sa_column=Column(timestamp.Timestamp))
    expiry: types.AuthCredential.expiry = Field(
        sa_column=Column(timestamp.Timestamp))

    name: types.ApiKey.name = Field()
    user: 'User' = Relationship(back_populates='api_keys')
    api_key_scopes: list['ApiKeyScope'] = Relationship(
        back_populates='api_key', cascade_delete=True)

    _CLAIMS_MAPPING = {
        **auth_credential.CLAIMS_MAPPING_BASE, **{'sub': 'id'}
    }

    # async def get_scope_ids(self, session: Session = None, c: client.Client = None) -> list[types.ScopeTypes.id]:
    #     return [api_key_scope.scope_id for api_key_scope in self.api_key_scopes]

    # @classmethod
    # async def is_available(cls, session: Session, api_key_available_admin: ApiKeyAdminAvailable) -> bool:
    #     return not session.exec(select(cls).where(cls._build_conditions(api_key_available_admin.model_dump()))).one_or_none()

    # @classmethod
    # async def api_get_is_available(cls, session: Session, api_key_available_admin: ApiKeyAdminAvailable) -> None:

    #     if not await cls.is_available(session, api_key_available_admin):
    #         raise HTTPException(
    #             status_code=status.HTTP_409_CONFLICT, detail=cls.already_exists_message())

    # @classmethod
    # async def _check_authorization_new(cls, params):
    #     if not params.admin:
    #         if params.authorized_user_id != params.create_model.user_id:
    #             raise HTTPException(
    #                 status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to post api key for another user')

    # async def _check_authorization_existing(self, params):
    #     if not params.admin:
    #         if self.user_id != params.authorized_user_id:
    #             raise self.not_found_exception()

    # @classmethod
    # async def _check_validation_post(cls, params):
    #     await cls.api_get_is_available(params.session, ApiKeyAdminAvailable(
    #         name=params.create_model.name, user_id=params.create_model.user_id)
    #     )

    # async def _check_validation_patch(self, params):
    #     if 'name' in params.update_model.model_fields_set:
    #         await self.api_get_is_available(params.session, ApiKeyAdminAvailable(
    #             name=params.update_model.name, user_id=params.authorized_user_id))

    @classmethod
    def _build_select_by_id(cls, id):
        return select(cls).where(cls.id == id)


class ApiKeyExport(BaseModel):
    id: types.ApiKey.id
    user_id: types.User.id
    name: types.ApiKey.name
    issued: types.ApiKey.issued
    expiry: types.ApiKey.expiry


class ApiKeyPublic(ApiKeyExport):
    pass


class ApiKeyPrivate(ApiKeyExport):
    scope_ids: list[types.Scope.id]

    @classmethod
    def from_api_key(cls, api_key: ApiKey) -> Self:
        return cls.model_construct(**api_key.model_dump(), scope_ids=[api_key_scope.scope_id for api_key_scope in api_key.api_key_scopes])
