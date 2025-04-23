from typing import Type, Literal, TypedDict, Protocol
from .tables import UserAccessToken, ApiKey, OTP
from ..schemas.sign_up import SignUp


class HasTable[T](Protocol):
    _TABLE: Type[T] = NotImplemented


AuthCredential = Type[UserAccessToken] | Type[ApiKey] | Type[OTP] | Type[SignUp]
AuthCredentialInstance = UserAccessToken | ApiKey | OTP | SignUp

AuthCredentialJwt = Type[UserAccessToken] | Type[ApiKey] | Type[SignUp]
AuthCredentialJwtInstance = UserAccessToken | ApiKey | SignUp

AuthCredentialTable = Type[UserAccessToken] | Type[ApiKey] | Type[OTP]
AuthCredentialTableInstance = UserAccessToken | ApiKey | OTP

AuthCredentialJwtAndTable = Type[UserAccessToken] | Type[ApiKey]
AuthCredentialJwtAndTableInstance = UserAccessToken | ApiKey
