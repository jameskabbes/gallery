from pydantic import ValidationInfo
import datetime as datetime_module
import typing
from .. import types

# this order is very important for circular imports
from .sign_up import SignUp
from .user import User
from .user_access_token import UserAccessToken
from .otp import OTP

from .gallery import Gallery
from .gallery_permission import GalleryPermission

from .file import File
from .image_file_metadata import ImageFileMetadata
from .image_version import ImageVersion


from .api_key import ApiKey
from .api_key_scope import ApiKeyScope

AuthCredentialClass = typing.Type[UserAccessToken] | typing.Type[ApiKey] | typing.Type[OTP] | typing.Type[SignUp]
AuthCredentialClassInstance = UserAccessToken | ApiKey | OTP | SignUp
AUTH_CREDENTIAL_CLASSES: set[AuthCredentialClass] = {
    UserAccessToken, ApiKey, OTP, SignUp}

AuthCredentialJwtType = typing.Literal['access_token', 'api_key', 'sign_up']
AuthCredentialJwtClass = typing.Type[UserAccessToken] | typing.Type[ApiKey] | typing.Type[SignUp]
AuthCredentialJwtClassInstance = UserAccessToken | ApiKey | SignUp
AUTH_CREDENTIAL_JWT_CLASSES: set[AuthCredentialJwtClass] = {
    UserAccessToken, ApiKey, SignUp}

AuthCredentialTableClass = typing.Type[UserAccessToken] | typing.Type[ApiKey] | typing.Type[OTP]
AuthCredentialTableClassInstance = UserAccessToken | ApiKey | OTP
AUTH_CREDENTIAL_TABLE_CLASSES: set[AuthCredentialTableClass] = {
    UserAccessToken, ApiKey, OTP}

AuthCredentialJwtAndTableClass = typing.Type[UserAccessToken] | typing.Type[ApiKey]
AuthCredentialJwtAndTableClassInstance = UserAccessToken | ApiKey
AUTH_CREDENTIAL_JWT_AND_TABLE_CLASSES: set[AuthCredentialJwtAndTableClass] = {
    UserAccessToken, ApiKey}


class T(typing.TypedDict):
    access_token: typing.Type[UserAccessToken]
    api_key: typing.Type[ApiKey]
    sign_up: typing.Type[SignUp]
    otp: typing.Type[OTP]


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
