from typing import Annotated, Literal, Union, NamedTuple
from pydantic import EmailStr, StringConstraints
import re
import datetime as datetime_module

PhoneNumber = str
Email = Annotated[EmailStr, StringConstraints(
    min_length=1, max_length=254)]
JwtEncodedStr = str


_IdType = Union[str, int, NamedTuple]

# typing.TypeVar(
#     '_IdType', bound=Union[str, int, typing.NamedTuple], covariant=True)


class PermissionLevel:
    id = int
    name = Literal['editor', 'viewer']


class VisibilityLevel:
    id = int
    name = Literal['public', 'private']


class Scope:
    id = int
    name = Literal['admin', 'users.read', 'users.write']


class UserRole:
    id = int
    name = Literal['admin', 'user']


class User:
    id = str
    email = Email
    phone_number = PhoneNumber

    password = Annotated[str, StringConstraints(
        min_length=1, max_length=64)]
    username = Annotated[str, StringConstraints(
        min_length=3, max_length=20, pattern=re.compile(r'^[a-zA-Z0-9_.-]+$'), to_lower=True)]
    hashed_password = str
    user_role_id = UserRole.id


class AuthCredential:
    issued = Annotated[datetime_module.datetime,
                       'The datetime at which the auth credential was issued']
    issued_timestamp = Annotated[float,
                                 'The datetime at which the auth credential was issued']
    expiry = Annotated[datetime_module.datetime,
                       'The datetime at which the auth credential will expire']
    expiry_timestamp = Annotated[float,
                                 'The datetime at which the auth credential will expire']
    type = Literal['access_token', 'api_key', 'otp', 'sign_up']


class OTP(AuthCredential):
    id = str
    code = Annotated[str, StringConstraints(
        min_length=6, max_length=6, pattern=re.compile(r'^\d{' + str(6) + r'}$'))]
    hashed_code = str


class UserAccessToken(AuthCredential):
    id = str


class ApiKey(AuthCredential):
    id = str
    name = Annotated[str, StringConstraints(
        min_length=1, max_length=256)]
    order_by = Literal['issued', 'expiry', 'name']


class SignUp(AuthCredential):
    email = User.email


class Gallery:
    class BaseTypes:
        id = str

    id = BaseTypes.id
    user_id = User.id

    # name can't start with the `YYYY-MM-DD ` pattern
    name = Annotated[str, StringConstraints(
        min_length=1, max_length=256, pattern=re.compile(r'^(?!\d{4}-\d{2}-\d{2} ).*'))]
    visibility_level = VisibilityLevel.id
    parent_id = BaseTypes.id
    description = Annotated[str, StringConstraints(
        min_length=0, max_length=20000)]
    date = datetime_module.date
    folder_name = str


class _GalleryPermissionBase:
    gallery_id = Gallery.id
    user_id = User.id
    permission_level = PermissionLevel.id


class GalleryPermissionId(NamedTuple):
    gallery_id: Gallery.BaseTypes.id
    user_id: User.id


class GalleryPermission(_GalleryPermissionBase):
    id = GalleryPermissionId


class _ApiKeyScopeBase:
    api_key_id = ApiKey.id
    scope_id = Scope.id


class ApiKeyScopeId(NamedTuple):
    api_key_id: ApiKey.id
    scope_id: Scope.id


class ApiKeyScope(_ApiKeyScopeBase):
    id = ApiKeyScopeId


class File:
    id = str
    stem = str
    suffix = Annotated[str, StringConstraints(
        to_lower=True)]
    size = int
    gallery_id = Gallery.id


class ImageVersion:

    class BaseTypes:
        id = str

    id = BaseTypes.id
    gallery_id = Gallery.id
    base_name = Annotated[str, StringConstraints(
        # prohibit underscore
        min_length=1, max_length=240, pattern=re.compile(r'^(?!.*_).+$')
    )]
    version = Annotated[str, StringConstraints(
        # version cannot be exactly two digits
        pattern=re.compile(r'^(?!\d{2}$).+$'))]
    parent_id = BaseTypes.id
    datetime = datetime_module.datetime
    description = Annotated[str, StringConstraints(
        min_length=0, max_length=20000)]
    aspect_ratio = float
    average_color = str


class ImageFileMetadata:
    file_id = File.id
    version_id = ImageVersion.id
    scale = int
