from typing import Type, Literal, TypedDict
from .tables import UserAccessToken, ApiKey, OTP
from .schemas.sign_up import SignUp


AuthCredentialClass = Type[UserAccessToken] | Type[ApiKey] | Type[OTP] | Type[SignUp]
AuthCredentialClassInstance = UserAccessToken | ApiKey | OTP | SignUp
AUTH_CREDENTIAL_CLASSES: set[AuthCredentialClass] = {
    UserAccessToken, ApiKey, OTP, SignUp}

AuthCredentialJwtType = Literal['access_token', 'api_key', 'sign_up']
AuthCredentialJwtClass = Type[UserAccessToken] | Type[ApiKey] | Type[SignUp]
AuthCredentialJwtClassInstance = UserAccessToken | ApiKey | SignUp
AUTH_CREDENTIAL_JWT_CLASSES: set[AuthCredentialJwtClass] = {
    UserAccessToken, ApiKey, SignUp}

AuthCredentialTableClass = Type[UserAccessToken] | Type[ApiKey] | Type[OTP]
AuthCredentialTableClassInstance = UserAccessToken | ApiKey | OTP
AUTH_CREDENTIAL_TABLE_CLASSES: set[AuthCredentialTableClass] = {
    UserAccessToken, ApiKey, OTP}

AuthCredentialJwtAndTableClass = Type[UserAccessToken] | Type[ApiKey]
AuthCredentialJwtAndTableClassInstance = UserAccessToken | ApiKey
AUTH_CREDENTIAL_JWT_AND_TABLE_CLASSES: set[AuthCredentialJwtAndTableClass] = {
    UserAccessToken, ApiKey}


class T(TypedDict):
    access_token: Type[UserAccessToken]
    api_key: Type[ApiKey]
    sign_up: Type[SignUp]
    otp: Type[OTP]


AUTH_CREDENTIAL_TYPE_TO_CLASS: T = {
    'access_token': UserAccessToken,
    'api_key': ApiKey,
    'sign_up': SignUp,
    'otp': OTP,
}

# 'access_token': UserAccessToken,
# 'api_key': ApiKey,
# 'otp': OTP,
# 'sign_up': SignUp
