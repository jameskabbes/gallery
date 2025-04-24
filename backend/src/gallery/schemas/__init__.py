from pydantic import BaseModel

from typing import Type
from ..models.tables import UserAccessToken, ApiKey, OTP
from ..schemas.sign_up import SignUp


class FromAttributes(BaseModel):
    class Config:
        from_attributes = True


AuthCredential = Type[UserAccessToken] | Type[ApiKey] | Type[OTP] | Type[SignUp]
AuthCredentialInstance = UserAccessToken | ApiKey | OTP | SignUp

AuthCredentialJwt = Type[UserAccessToken] | Type[ApiKey] | Type[SignUp]
AuthCredentialJwtInstance = UserAccessToken | ApiKey | SignUp

AuthCredentialTable = Type[UserAccessToken] | Type[ApiKey] | Type[OTP]
AuthCredentialTableInstance = UserAccessToken | ApiKey | OTP

AuthCredentialJwtAndTable = Type[UserAccessToken] | Type[ApiKey]
AuthCredentialJwtAndTableInstance = UserAccessToken | ApiKey
