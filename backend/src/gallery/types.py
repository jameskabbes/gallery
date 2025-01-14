import typing
from pydantic import EmailStr, StringConstraints


PhoneNumber = str
Email = typing.Annotated[EmailStr, StringConstraints(
    min_length=1, max_length=254)]
JwtEncodedStr = str


class PermissionLevelTypes:
    id = int
    name = typing.Literal['editor', 'viewer']


class VisibilityLevelTypes:
    id = int
    name = typing.Literal['public', 'private']


class ScopeTypes:
    id = int
    name = typing.Literal['admin', 'users.read', 'users.write']


class UserRoleTypes:
    id = int
    name = typing.Literal['admin', 'user']
