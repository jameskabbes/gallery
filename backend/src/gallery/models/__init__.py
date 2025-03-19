from pydantic import ValidationInfo
import datetime as datetime_module
import typing
from gallery import types
from .user import User
from .user_access_token import UserAccessToken
from .sign_up import SignUp
from .otp import OTP
from .image_version import ImageVersion
from .image_file_metadata import ImageFileMetadata
from .gallery import Gallery
from .gallery_permission import GalleryPermission
from .file import File
from .api_key import ApiKey
from .api_key_scope import ApiKeyScope


AuthCredentialClasses = typing.Type[UserAccessToken] | typing.Type[ApiKey] | typing.Type[OTP] | typing.Type[SignUp]
AUTH_CREDENTIAL_CLASSES: set[AuthCredentialClasses] = {
    UserAccessToken, ApiKey, OTP, SignUp}

AuthCredentialTokenType = typing.Literal['access_token', 'api_key', 'sign_up']
AuthCredentialTokenClass = typing.Type[UserAccessToken] | typing.Type[ApiKey] | typing.Type[SignUp]
AUTH_CREDENTIAL_TOKEN_CLASSES: set[AuthCredentialTokenClass] = {
    UserAccessToken, ApiKey, SignUp}

AuthCredentialTableClass = typing.Type[UserAccessToken] | typing.Type[ApiKey] | typing.Type[OTP]
AUTH_CREDENTIAL_TABLE_CLASSES: set[AuthCredentialTableClass] = {
    UserAccessToken, ApiKey, OTP}

AUTH_CREDENTIAL_TYPE_TO_CLASS: dict[types.AuthCredential.type, AuthCredentialClasses] = {
    'access_token': UserAccessToken,
    'api_key': ApiKey,
    'otp': OTP,
    'sign_up': SignUp
}
