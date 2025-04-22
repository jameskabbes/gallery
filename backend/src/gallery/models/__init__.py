from typing import Type, Literal, TypedDict, Protocol
from .tables import UserAccessToken, ApiKey, OTP
from ..schemas.sign_up import SignUp


class HasTable[T](Protocol):
    _TABLE: Type[T] = NotImplemented


AuthCredentialModel = Type[UserAccessToken] | Type[ApiKey] | Type[OTP] | Type[SignUp]
AuthCredentialModelInstance = UserAccessToken | ApiKey | OTP | SignUp

AuthCredentialJwtModel = Type[UserAccessToken] | Type[ApiKey] | Type[SignUp]
AuthCredentialJwtModelInstance = UserAccessToken | ApiKey | SignUp

AuthCredentialTableModel = Type[UserAccessToken] | Type[ApiKey] | Type[OTP]
AuthCredentialTableModelInstance = UserAccessToken | ApiKey | OTP

AuthCredentialJwtAndTableModel = Type[UserAccessToken] | Type[ApiKey]
AuthCredentialJwtAndTableModelInstance = UserAccessToken | ApiKey
