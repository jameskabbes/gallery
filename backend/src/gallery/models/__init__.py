from .api_key_scope import ApiKeyScope
from .api_key import ApiKey
from .file import File
from .gallery_permission import GalleryPermission
from .gallery import Gallery
from .image_file_metadata import ImageFileMetadata
from .image_version import ImageVersion
from .otp import OTP
from .sign_up import SignUp
from .user_access_token import UserAccessToken
from .user import User

from gallery import types
import typing
from pydantic import BaseModel
import datetime as datetime_module
from pydantic import ValidationInfo


class Pagination(BaseModel):
    limit: int
    offset: int


def validate_and_normalize_datetime(value: datetime_module.datetime, info: ValidationInfo) -> datetime_module.datetime:
    if value.tzinfo == None:
        raise ValueError(str(info.field_name) + ' must have a timezone')
    return value.astimezone(datetime_module.timezone.utc)


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
