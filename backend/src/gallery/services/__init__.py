from typing import Type, TypedDict, Literal

from .api_key import ApiKey as ApiKeyService
from .otp import OTP as OTPService
from .user_access_token import UserAccessToken as UserAccessTokenService
from .sign_up import SignUp as SignUpService

from .. import types

AuthCredentialService = Type[UserAccessTokenService] | Type[ApiKeyService] | Type[OTPService] | Type[SignUpService]
AuthCredentialJwtService = Type[UserAccessTokenService] | Type[ApiKeyService] | Type[SignUpService]


AUTH_CREDENTIAL_JWT_SERVICES: set[AuthCredentialJwtService] = {
    UserAccessTokenService,
    ApiKeyService,
    SignUpService,
}


AuthCredentialTableService = Type[UserAccessTokenService] | Type[ApiKeyService] | Type[OTPService]
AuthCredentialJwtAndTableService = Type[UserAccessTokenService] | Type[ApiKeyService]

AuthCredentialJwtAndNotTableService = Type[SignUpService]
AuthCredentialNotJwtAndTableService = Type[OTPService]


class AuthCredentialTypeToService(TypedDict):
    access_token: Type[UserAccessTokenService]
    api_key: Type[ApiKeyService]
    sign_up: Type[SignUpService]
    otp: Type[OTPService]


AUTH_CREDENTIAL_TYPE_TO_SERVICE: AuthCredentialTypeToService = {
    'access_token': UserAccessTokenService,
    'api_key': ApiKeyService,
    'sign_up': SignUpService,
    'otp': OTPService,
}
