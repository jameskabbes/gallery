from sqlmodel import select
from pydantic import BaseModel
import string
import secrets
import datetime as datetime_module

from ..models.tables import OTP as OTPTable
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
        auth_credential_service.Table[OTPTable]):

    auth_type = 'otp'
    _TABLE = OTPTable

    @classmethod
    def _table_sub(cls, inst):
        return inst.id

    @classmethod
    async def table_inst_from_create_model(cls, create_model):

        return cls._TABLE(
            id=utils.generate_uuid(),
            issued=datetime_module.datetime.now().astimezone(datetime_module.UTC),
            **create_model.model_dump()
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
