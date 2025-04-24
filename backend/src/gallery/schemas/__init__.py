from pydantic import BaseModel

from typing import Type, Literal
from ..models.tables import UserAccessToken, ApiKey, OTP
from ..schemas.sign_up import SignUp


class FromAttributes(BaseModel):
    class Config:
        from_attributes = True


AuthCredential = Type[UserAccessToken] | Type[ApiKey] | Type[OTP] | Type[SignUp]
AuthCredentialType = Literal['access_token', 'api_key', 'otp', 'sign_up']
AuthCredentialInstance = UserAccessToken | ApiKey | OTP | SignUp

AUTH_CREDENTIAL_TYPES: set[AuthCredentialType] = {
    'access_token',
    'api_key',
    'otp',
    'sign_up',
}


AuthCredentialJwt = Type[UserAccessToken] | Type[ApiKey] | Type[SignUp]
AuthCredentialJwtType = Literal['access_token', 'api_key', 'sign_up']
AuthCredentialJwtInstance = UserAccessToken | ApiKey | SignUp

AuthCredentialTable = Type[UserAccessToken] | Type[ApiKey] | Type[OTP]
AuthCredentialTableType = Literal['access_token', 'api_key', 'otp']
AuthCredentialTableInstance = UserAccessToken | ApiKey | OTP

AuthCredentialJwtAndTable = Type[UserAccessToken] | Type[ApiKey]
AuthCredentialJwtAndTableType = Literal['access_token', 'api_key']
AuthCredentialJwtAndTableInstance = UserAccessToken | ApiKey

PrimaryAuthCredential = Type[UserAccessToken] | Type[ApiKey]
PrimaryAuthCredentialInstance = UserAccessToken | ApiKey
