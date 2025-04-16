from sqlmodel import Field, Relationship, select, SQLModel
from typing import TYPE_CHECKING, TypedDict, Optional
from pydantic import BaseModel
from sqlalchemy import Column

from .. import types, utils
from .bases.table import Table as BaseTable
from .bases import auth_credential
from ..config import settings
from .custom_field_types import timestamp

ID_COL = 'id'

if TYPE_CHECKING:
    from . import user


class UserAccessTokenAdminUpdate(BaseModel):
    pass


class UserAccessTokenAdminCreate(auth_credential.Create):
    user_id: types.User.id


class JwtPayload(auth_credential.JwtPayloadBase):
    sub: types.User.id


class JwtModel(auth_credential.JwtModelBase):
    id: types.User.id


class UserAccessToken(
        BaseTable[types.UserAccessToken.id, UserAccessTokenAdminCreate,
                  UserAccessTokenAdminUpdate],
        auth_credential.Table,
        auth_credential.Model,
        auth_credential.JwtIO[JwtPayload, JwtModel],
        table=True):

    __tablename__ = 'user_access_token'  # type: ignore

    auth_type = 'access_token'
    _ROUTER_TAG = 'User Access Token'
    _CLAIMS_MAPPING = {
        **auth_credential.CLAIMS_MAPPING_BASE, **{'sub': 'id'}
    }

    id: types.ImageVersion.id = Field(
        primary_key=True, index=True, unique=True, const=True)
    issued: types.AuthCredential.issued = Field(
        const=True, sa_column=Column(timestamp.Timestamp))
    expiry: types.AuthCredential.expiry = Field(
        sa_column=Column(timestamp.Timestamp))
    user: 'user.User' = Relationship(back_populates='user_access_tokens')

    # @classmethod
    # async def _check_authorization_new(cls, params):

    #     if not params.admin:
    #         if params.authorized_user_id != params.create_model.user_id:
    #             raise HTTPException(
    #                 status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to post access token for another user')

    # async def _check_authorization_existing(self, params):
    #     if not params.admin:
    #         if self.user_id != params.authorized_user_id:
    #             raise self.not_found_exception()

    # async def get_scope_ids(self, session: Session = None) -> list[types.ScopeTypes.id]:
    #     return config.USER_ROLE_ID_SCOPE_IDS[self.user.user_role_id]


'''
# UserAccessToken

class UserAccessTokenTypes(AuthCredentialTypes):
    id = str


class UserAccessTokenUserAccessTokenIdBase(UserAccessTokenIdObject[UserAccessTokenTypes.id]):
    id: UserAccessTokenTypes.id = Field(
        primary_key=True, index=True, unique=True, const=True)


class UserAccessTokenUserAccessTokenAdminUpdate(BaseModel):
    pass


class UserAccessTokenAdminCreate(AuthCredential.Create):
    user_id: types.User.id


class UserAccessTokenJwt:
    class Encode(AuthCredential.JwtEncodeBase):
        sub: types.User.id

    class Decode(AuthCredential.JwtDecodeBase):
        id: types.User.id


class UserAccessToken(
        Table['UserAccessToken', UserAccessTokenTypes.id, UserAccessTokenAdminCreate,
              BaseModel, BaseModel, UserAccessTokenUserAccessTokenAdminUpdate, BaseModel, BaseModel, typing.Literal[()]],
        AuthCredential.Table,
        AuthCredential.JwtIO[UserAccessTokenJwt.Encode,
                             UserAccessTokenJwt.Decode],
        AuthCredential.Model,
        UserAccessTokenUserAccessTokenIdBase,
        table=True):

    auth_type = 'access_token'
    __tablename__ = 'user_access_token'

    issued: AuthCredentialTypes.issued = Field(
        const=True, sa_column=Column(DateTimeWithTimeZoneString))
    expiry: AuthCredentialTypes.expiry = Field(
        sa_column=Column(DateTimeWithTimeZoneString))

    user: 'User' = Relationship(
        back_populates='user_access_tokens')

    _JWT_CLAIMS_MAPPING = {
        **AuthCredential.Model._JWT_CLAIMS_MAPPING_BASE, **{'sub': 'id'}}
    _ROUTER_TAG: typing.ClassVar[str] = 'User Access Token'

    @classmethod
    async def _check_authorization_new(cls, params):

        if not params.admin:
            if params.authorized_user_id != params.create_model.user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to post access token for another user')

    async def _check_authorization_existing(self, params):
        if not params.admin:
            if self.user_id != params.authorized_user_id:
                raise self.not_found_exception()

    async def get_scope_ids(self, session: Session = None) -> list[types.ScopeTypes.id]:
        return config.USER_ROLE_ID_SCOPE_IDS[self.user.user_role_id]
'''
