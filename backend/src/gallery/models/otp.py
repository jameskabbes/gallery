from sqlmodel import Field, Relationship, select, SQLModel
from typing import TYPE_CHECKING, TypedDict, Optional
from gallery import types, utils
from gallery.models.bases.table import Table as BaseTable
from gallery.models.bases import auth_credential
from gallery.config import settings
from pydantic import BaseModel
import string
import secrets

if TYPE_CHECKING:
    from gallery.models.user import User

ID_COL = 'id'


class Id(SQLModel):
    id: types.OTP.id


class AdminUpdate(BaseModel):
    pass


class AdminCreate(auth_credential.Create):
    user_id: types.User.id
    hashed_code: types.OTP.hashed_code


class OTP(
        BaseTable['OTP', Id],
        auth_credential.Table,
        auth_credential.Model,
        table=True):

    auth_type = 'otp'

    id: types.OTP.id = Field(primary_key=True, index=True, unique=True)
    # issued: types.OTP.issued = Field(
    #     const=True, sa_column=Column(DateTimeWithTimeZoneString))
    # expiry: AuthCredentialTypes.expiry = Field(
    #     sa_column=Column(DateTimeWithTimeZoneString))

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
    def _build_get_by_id_query(cls, id: Id):
        return select(cls).where(cls.id == id.id)


'''

# OTP


class OTPConfig:
    CODE_LENGTH: typing.ClassVar[int] = 6


class OTPTypes(AuthCredentialTypes):
    id = str
    code = typing.Annotated[str, StringConstraints(
        min_length=OTPConfig.CODE_LENGTH, max_length=OTPConfig.CODE_LENGTH, pattern=re.compile(r'^\d{6}$'))]
    hashed_code = str


class OTPIdBase(IdObject[OTPTypes.id]):
    id: OTPTypes.id = Field(
        primary_key=True, index=True, unique=True, const=True)


class OTPAdminUpdate(BaseModel):
    pass


class OTPAdminCreate(AuthCredential.Create):
    user_id: types.User.id
    hashed_code: OTPTypes.hashed_code


class OTP(
        Table['OTP', OTPTypes.id,
              OTPAdminCreate, BaseModel, BaseModel, OTPAdminUpdate, BaseModel, BaseModel, typing.Literal[()]],
        AuthCredential.Table,
        AuthCredential.Model,
        OTPIdBase,
        table=True):

    auth_type = 'otp'
    __tablename__ = 'otp'

    issued: AuthCredentialTypes.issued = Field(
        const=True, sa_column=Column(DateTimeWithTimeZoneString))
    expiry: AuthCredentialTypes.expiry = Field(
        sa_column=Column(DateTimeWithTimeZoneString))

    hashed_code: OTPTypes.hashed_code = Field()
    user: 'User' = Relationship(
        back_populates='otps')

    _ROUTER_TAG = 'One Time Password'

    @classmethod
    def generate_code(cls) -> OTPTypes.code:
        characters = string.digits
        return ''.join(secrets.choice(characters) for _ in range(OTPConfig.CODE_LENGTH))

    @classmethod
    def hash_code(cls, code: OTPTypes.code) -> OTPTypes.hashed_code:
        return utils.hash_password(code)

    @classmethod
    def verify_code(cls, code: OTPTypes.code, hashed_code: OTPTypes.hashed_code) -> bool:

        import time
        start = time.time()
        a = utils.verify_password(code, hashed_code)
        end = time.time()
        print(end - start)
        return a

'''
