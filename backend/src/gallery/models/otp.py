from sqlmodel import Field, Relationship, select, SQLModel
from typing import TYPE_CHECKING, TypedDict, Optional
from pydantic import BaseModel
import string
import secrets
from sqlalchemy import Column
from .custom_field_types import timestamp
from .. import types, utils
from .bases import table, auth_credential
from ..config import settings

ID_COL = 'id'

if TYPE_CHECKING:
    from .user import User


class OTPAdminUpdate(BaseModel):
    pass


class OTPAdminCreate(auth_credential.Create):
    user_id: types.User.id
    hashed_code: types.OTP.hashed_code


class OTP(
        table.Table[
            types.OTP.id,
            OTPAdminCreate,
            OTPAdminUpdate,
            table.AfterCreateCustomParams,
            table.AfterReadCustomParams,
            table.AfterUpdateCustomParams,
            table.AfterDeleteCustomParams],
        auth_credential.Table,
        table=True):

    __tablename__ = 'otp'  # type: ignore

    auth_type = 'otp'

    id: types.OTP.id = Field(
        primary_key=True, index=False, unique=True, const=True)
    issued: types.AuthCredential.issued = Field(
        const=True, sa_column=Column(timestamp.Timestamp))
    expiry: types.AuthCredential.expiry = Field(
        sa_column=Column(timestamp.Timestamp))

    hashed_code: types.OTP.hashed_code = Field()
    user: 'User' = Relationship(
        back_populates='otps')

    _ROUTER_TAG = 'One Time Password'

    @classmethod
    def generate_code(cls) -> types.OTP.code:
        characters = string.digits
        return ''.join(secrets.choice(characters) for _ in range(settings.OTP_LENGTH))

    @classmethod
    def hash_code(cls, code: types.OTP.code) -> types.OTP.hashed_code:
        return utils.hash_password(code)

    @classmethod
    def verify_code(cls, code: types.OTP.code, hashed_code: types.OTP.hashed_code) -> bool:

        import time
        start = time.time()
        a = utils.verify_password(code, hashed_code)
        end = time.time()
        print(end - start)
        return a

    @classmethod
    def _build_select_by_id(cls, id):
        return select(cls).where(cls.id == id)


# # OTP


# class OTPConfig:
#     CODE_LENGTH: typing.ClassVar[int] = 6


# class OTPTypes(AuthCredentialTypes):
#     id = str
#     code = typing.Annotated[str, StringConstraints(
#         min_length=OTPConfig.CODE_LENGTH, max_length=OTPConfig.CODE_LENGTH, pattern=re.compile(r'^\d{6}$'))]
#     hashed_code = str


# class OTPOTPIdBase(OTPIdObject[OTPTypes.id]):
#     id: OTPTypes.id = Field(
#         primary_key=True, index=True, unique=True, const=True)


# class OTPAdminUpdate(BaseModel):
#     pass


# class OTPOTPAdminCreate(AuthCredential.Create):
#     user_id: types.User.id
#     hashed_code: OTPTypes.hashed_code


# class OTP(
#         Table['OTP', OTPTypes.id,
#               OTPOTPAdminCreate, BaseModel, BaseModel, OTPAdminUpdate, BaseModel, BaseModel, typing.Literal[()]],
#         AuthCredential.Table,
#         AuthCredential.Model,
#         OTPOTPIdBase,
#         table=True):

#     auth_type = 'otp'
#     __tablename__ = 'otp'

#     issued: AuthCredentialTypes.issued = Field(
#         const=True, sa_column=Column(DateTimeWithTimeZoneString))
#     expiry: AuthCredentialTypes.expiry = Field(
#         sa_column=Column(DateTimeWithTimeZoneString))

#     hashed_code: OTPTypes.hashed_code = Field()
#     user: 'User' = Relationship(
#         back_populates='otps')

#     _ROUTER_TAG = 'One Time Password'

#     @classmethod
#     def generate_code(cls) -> OTPTypes.code:
#         characters = string.digits
#         return ''.join(secrets.choice(characters) for _ in range(OTPConfig.CODE_LENGTH))

#     @classmethod
#     def hash_code(cls, code: OTPTypes.code) -> OTPTypes.hashed_code:
#         return utils.hash_password(code)

#     @classmethod
#     def verify_code(cls, code: OTPTypes.code, hashed_code: OTPTypes.hashed_code) -> bool:

#         import time
#         start = time.time()
#         a = utils.verify_password(code, hashed_code)
#         end = time.time()
#         print(end - start)
#         return a
