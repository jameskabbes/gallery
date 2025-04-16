import typing
from pydantic import EmailStr, StringConstraints
import re
import datetime as datetime_module

PhoneNumber = str
Email = typing.Annotated[EmailStr, StringConstraints(
    min_length=1, max_length=254)]
JwtEncodedStr = str


_IdType = typing.Union[str, int, typing.NamedTuple]

# typing.TypeVar(
#     '_IdType', bound=typing.Union[str, int, typing.NamedTuple], covariant=True)


class PermissionLevel:
    id = int
    name = typing.Literal['editor', 'viewer']


class VisibilityLevel:
    id = int
    name = typing.Literal['public', 'private']


class Scope:
    id = int
    name = typing.Literal['admin', 'users.read', 'users.write']


class UserRole:
    id = int
    name = typing.Literal['admin', 'user']


class User:
    id = str
    email = Email
    phone_number = PhoneNumber

    password = typing.Annotated[str, StringConstraints(
        min_length=1, max_length=64)]
    username = typing.Annotated[str, StringConstraints(
        min_length=3, max_length=20, pattern=re.compile(r'^[a-zA-Z0-9_.-]+$'), to_lower=True)]
    hashed_password = str
    user_role_id = UserRole.id


class AuthCredential:
    issued = typing.Annotated[datetime_module.datetime,
                              'The datetime at which the auth credential was issued']
    issued_timestamp = typing.Annotated[float,
                                        'The datetime at which the auth credential was issued']
    expiry = typing.Annotated[datetime_module.datetime,
                              'The datetime at which the auth credential will expire']
    expiry_timestamp = typing.Annotated[float,
                                        'The datetime at which the auth credential will expire']
    type = typing.Literal['access_token', 'api_key', 'otp', 'sign_up']


class OTP(AuthCredential):
    id = str
    code = typing.Annotated[str, StringConstraints(
        min_length=6, max_length=6, pattern=re.compile(r'^\d{' + str(6) + r'}$'))]
    hashed_code = str


class UserAccessToken(AuthCredential):
    id = str


class ApiKey(AuthCredential):
    id = str
    name = typing.Annotated[str, StringConstraints(
        min_length=1, max_length=256)]
    order_by = typing.Literal['issued', 'expiry', 'name']


class Gallery:
    class BaseTypes:
        id = str

    id = BaseTypes.id
    user_id = User.id

    # name can't start with the `YYYY-MM-DD ` pattern
    name = typing.Annotated[str, StringConstraints(
        min_length=1, max_length=256, pattern=re.compile(r'^(?!\d{4}-\d{2}-\d{2} ).*'))]
    visibility_level = VisibilityLevel.id
    parent_id = BaseTypes.id
    description = typing.Annotated[str, StringConstraints(
        min_length=0, max_length=20000)]
    date = datetime_module.date
    folder_name = str


class _GalleryPermissionBase:
    gallery_id = Gallery.id
    user_id = User.id
    permission_level = PermissionLevel.id


class GalleryPermissionId(typing.NamedTuple):
    gallery_id: Gallery.BaseTypes.id
    user_id: User.id


class GalleryPermission(_GalleryPermissionBase):
    id = GalleryPermissionId


class _ApiKeyScopeBase:
    api_key_id = ApiKey.id
    scope_id = Scope.id


class ApiKeyScopeId(typing.NamedTuple):
    api_key_id: ApiKey.id
    scope_id: Scope.id


class ApiKeyScope(_ApiKeyScopeBase):
    id = ApiKeyScopeId


class File:
    id = str
    stem = str
    suffix = typing.Annotated[str, StringConstraints(
        to_lower=True)]
    size = int
    gallery_id = Gallery.id


class ImageVersion:

    class BaseTypes:
        id = str

    id = BaseTypes.id
    gallery_id = Gallery.id
    base_name = typing.Annotated[str, StringConstraints(
        # prohibit underscore
        min_length=1, max_length=240, pattern=re.compile(r'^(?!.*_).+$')
    )]
    version = typing.Annotated[str, StringConstraints(
        # version cannot be exactly two digits
        pattern=re.compile(r'^(?!\d{2}$).+$'))]
    parent_id = BaseTypes.id
    datetime = datetime_module.datetime
    description = typing.Annotated[str, StringConstraints(
        min_length=0, max_length=20000)]
    aspect_ratio = float
    average_color = str


class ImageFileMetadata:
    file_id = File.id
    version_id = ImageVersion.id
    scale = int
