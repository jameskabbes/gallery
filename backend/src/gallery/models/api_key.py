from sqlmodel import Field, Relationship, select, SQLModel
from sqlalchemy import Column
from typing import TYPE_CHECKING, TypedDict, Optional
from gallery import types, utils
from gallery.models.bases.table import Table as BaseTable
from gallery.models.bases import auth_credential
from pydantic import BaseModel

ID_COL = 'id'


class Id(SQLModel):
    id: types.ApiKey.id = Field(
        primary_key=True, index=True, unique=True, const=True)


class Available(BaseModel):
    name: types.ApiKey.name


class AdminAvailable(Available):
    user_id: types.User.id


class Import(auth_credential.Import):
    pass


class Update(Import, auth_credential.Update):
    name: Optional[types.ApiKey.name] = None


class AdminUpdate(Update):
    pass


class Create(Import, auth_credential.Create):
    name: types.ApiKey.name


class AdminCreate(Create):
    user_id: types.User.id


class JwtPayload(auth_credential.JwtPayloadBase):
    sub: types.User.id


class JwtModel(auth_credential.JwtModelBase):
    id: types.User.id


class ApiKey(
        BaseTable['ApiKey', Id],
        Id,
        auth_credential.Table,
        auth_credential.Model,
        auth_credential.JwtIO[JwtPayload, JwtModel],
        table=True):

    auth_type = 'api_key'
    _ROUTER_TAG = 'Api Key'

    # issued: types.AuthCredential.issued = Field(
    #     const=True, sa_column=Column(DateTimeWithTimeZoneString))
    # expiry: auth_credentialTypes.expiry = Field(
    #     sa_column=Column(DateTimeWithTimeZoneString))

    name: types.ApiKey.name = Field()
    # user: 'User' = Relationship(back_populates='api_keys')
    # api_key_scopes: list['ApiKeyScope'] = Relationship(
    #     back_populates='api_key', cascadedelete=True)

    _CLAIMS_MAPPING = {
        **auth_credential.CLAIMS_MAPPING_BASE, **{'sub': 'id'}
    }

    # async def get_scope_ids(self, session: Session = None, c: client.Client = None) -> list[types.ScopeTypes.id]:
    #     return [api_key_scope.scope_id for api_key_scope in self.api_key_scopes]

    # @classmethod
    # async def is_available(cls, session: Session, api_key_available_admin: AdminAvailable) -> bool:
    #     return not session.exec(select(cls).where(cls._build_conditions(api_key_available_admin.model_dump()))).one_or_none()

    # @classmethod
    # async def api_get_is_available(cls, session: Session, api_key_available_admin: AdminAvailable) -> None:

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
    #     await cls.api_get_is_available(params.session, AdminAvailable(
    #         name=params.create_model.name, user_id=params.create_model.user_id)
    #     )

    # async def _check_validation_patch(self, params):
    #     if 'name' in params.update_model.model_fields_set:
    #         await self.api_get_is_available(params.session, AdminAvailable(
    #             name=params.update_model.name, user_id=params.authorized_user_id))


# class Export(ApiExport):
#     id: types.ApiKey.id
#     user_id: types.User.id
#     name: types.ApiKey.name
#     issued: types.ApiKey.issued
#     expiry: types.ApiKey.expiry


# class ApiKeyPublic(ApiKeyExport):
#     pass


# class ApiKeyPrivate(ApiKeyExport):
#     scope_ids: list[types.ScopeTypes.id]

#     @classmethod
#     def from_api_key(cls, api_key: ApiKey) -> typing.Self:
#         return cls.model_construct(**api_key.model_dump(), scope_ids=[api_key_scope.scope_id for api_key_scope in api_key.api_key_scopes])


'''
# ApiKey


class ApiKeyTypes(AuthCredentialTypes):
    id = str
    name = typing.Annotated[str, StringConstraints(
        min_length=1, max_length=256)]
    order_by = typing.Literal['issued', 'expiry', 'name']


class ApiKeyIdBase(IdObject[ApiKeyTypes.id]):
    id: ApiKeyTypes.id = Field(
        primary_key=True, index=True, unique=True, const=True)


class ApiKeyAvailable(BaseModel):
    name: ApiKeyTypes.name


class ApiKeyAdminAvailable(ApiKeyAvailable):
    user_id: types.User.id


class ApiKeyImport(AuthCredential.Import):
    pass


class ApiKeyUpdate(ApiKeyImport, AuthCredential.Update):
    name: typing.Optional[ApiKeyTypes.name] = None


class ApiKeyAdminUpdate(ApiKeyUpdate):
    pass


class ApiKeyCreate(ApiKeyImport, AuthCredential.Create):
    name: ApiKeyTypes.name


class ApiKeyAdminCreate(ApiKeyCreate):
    user_id: types.User.id


class ApiKeyJwt:
    class Encode(AuthCredential.JwtEncodeBase):
        sub: types.User.id

    class Decode(AuthCredential.JwtDecodeBase):
        id: types.User.id


class ApiKey(
        Table['ApiKey', ApiKeyTypes.id,
              ApiKeyAdminCreate, BaseModel, BaseModel,  ApiKeyAdminUpdate, BaseModel, BaseModel, ApiKeyTypes.order_by],
        AuthCredential.Table,
        AuthCredential.JwtIO[ApiKeyJwt.Encode, ApiKeyJwt.Decode],
        AuthCredential.Model,
        ApiKeyIdBase,
        table=True):
    auth_type = 'api_key'
    __tablename__ = 'api_key'

    issued: AuthCredentialTypes.issued = Field(
        const=True, sa_column=Column(DateTimeWithTimeZoneString))
    expiry: AuthCredentialTypes.expiry = Field(
        sa_column=Column(DateTimeWithTimeZoneString))

    name: ApiKeyTypes.name = Field()
    user: 'User' = Relationship(back_populates='api_keys')
    api_key_scopes: list['ApiKeyScope'] = Relationship(
        back_populates='api_key', cascadedelete=True)

    _JWT_CLAIMS_MAPPING = {
        **AuthCredential.Model._JWT_CLAIMS_MAPPING_BASE, **{'sub': 'id'}}

    _ROUTER_TAG = 'Api Key'

    async def get_scope_ids(self, session: Session = None, c: client.Client = None) -> list[types.ScopeTypes.id]:
        return [api_key_scope.scope_id for api_key_scope in self.api_key_scopes]

    @classmethod
    async def is_available(cls, session: Session, api_key_available_admin: ApiKeyAdminAvailable) -> bool:
        return not session.exec(select(cls).where(cls._build_conditions(api_key_available_admin.model_dump()))).one_or_none()

    @classmethod
    async def api_get_is_available(cls, session: Session, api_key_available_admin: ApiKeyAdminAvailable) -> None:

        if not await cls.is_available(session, api_key_available_admin):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=cls.already_exists_message())

    @classmethod
    async def _check_authorization_new(cls, params):
        if not params.admin:
            if params.authorized_user_id != params.create_model.user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to post api key for another user')

    async def _check_authorization_existing(self, params):
        if not params.admin:
            if self.user_id != params.authorized_user_id:
                raise self.not_found_exception()

    @classmethod
    async def _check_validation_post(cls, params):
        await cls.api_get_is_available(params.session, ApiKeyAdminAvailable(
            name=params.create_model.name, user_id=params.create_model.user_id)
        )

    async def _check_validation_patch(self, params):
        if 'name' in params.update_model.model_fields_set:
            await self.api_get_is_available(params.session, ApiKeyAdminAvailable(
                name=params.update_model.name, user_id=params.authorized_user_id))


class ApiKeyExport(TableExport):
    id: ApiKeyTypes.id
    user_id: types.User.id
    name: ApiKeyTypes.name
    issued: ApiKeyTypes.issued
    expiry: ApiKeyTypes.expiry


class ApiKeyPublic(ApiKeyExport):
    pass


class ApiKeyPrivate(ApiKeyExport):
    scope_ids: list[types.ScopeTypes.id]

    @classmethod
    def from_api_key(cls, api_key: ApiKey) -> typing.Self:
        return cls.model_construct(**api_key.model_dump(), scope_ids=[api_key_scope.scope_id for api_key_scope in api_key.api_key_scopes])

'''
