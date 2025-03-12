import typing
from pydantic import EmailStr, StringConstraints
import re

PhoneNumber = str
Email = typing.Annotated[EmailStr, StringConstraints(
    min_length=1, max_length=254)]
JwtEncodedStr = str


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
