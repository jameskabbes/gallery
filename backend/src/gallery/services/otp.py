from sqlmodel import select
from pydantic import BaseModel
import string
import secrets
import datetime as datetime_module

from ..models import OTP as OTPTable
from ..config import settings
from .. import utils, types
from . import base

from ..schemas import otp as otp_schema
from ..services import auth_credential as auth_credential_service


class OTP(
        base.Service[
            OTPTable,
            types.OTP.id,
            otp_schema.OTPAdminCreate,
            otp_schema.OTPAdminUpdate,
        ],
        auth_credential_service.Table[OTPTable, otp_schema.OTPAdminCreate]):

    _CLAIMS_MAPPING = {
        **auth_credential_service.CLAIMS_MAPPING_BASE, **{'sub': 'id'}
    }

    auth_type = 'otp'

    _TABLE = OTPTable

    @classmethod
    async def table_inst_from_create_model(cls, create_model: otp_schema.OTPAdminCreate) -> OTPTable:

        return cls._TABLE(
            id=utils.generate_uuid(),
            issued=datetime_module.datetime.now(datetime_module.timezone.utc),
            **create_model.model_dump(exclude_unset=True, exclude_defaults=True, exclude_none=True)
        )

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
        return select(cls._TABLE).where(cls._TABLE.id == id)


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
