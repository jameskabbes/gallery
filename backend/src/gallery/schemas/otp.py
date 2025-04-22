from pydantic import BaseModel
from typing import Optional

from .. import types
from ..schemas import auth_credential as auth_credential_schema


class OTPAdminUpdate(BaseModel):
    pass


class OTPAdminCreate(auth_credential_schema.Create):
    user_id: types.User.id
    hashed_code: types.OTP.hashed_code
