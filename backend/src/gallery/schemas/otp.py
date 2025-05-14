from pydantic import BaseModel
from typing import Optional

from gallery import types
from gallery.schemas import auth_credential as auth_credential_schema


class OTPAdminUpdate(BaseModel):
    pass


class OTPAdminCreate(BaseModel):
    user_id: types.User.id
    hashed_code: types.OTP.hashed_code
    expiry: types.AuthCredential.expiry
