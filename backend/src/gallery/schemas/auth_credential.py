from sqlmodel import SQLModel
from pydantic import BaseModel, field_serializer, field_validator, ValidationInfo, Field
from typing import TypedDict, Protocol, ClassVar, TypeVar
from .. import types
from ..models.tables import User
import datetime as datetime_module
from ..models.custom_field_types import timestamp


class JwtModel(TypedDict):
    expiry: types.AuthCredential.expiry_timestamp
    issued: types.AuthCredential.issued_timestamp
    type: types.AuthCredential.type


class JwtPayload(TypedDict):
    exp: types.AuthCredential.expiry_timestamp
    iat: types.AuthCredential.issued_timestamp
    type: types.AuthCredential.type


class HasAuthType(Protocol):
    auth_type: ClassVar[types.AuthCredential.type]


class HasUser(Protocol):
    user: User


class Model(SQLModel):
    issued: types.AuthCredential.issued
    expiry: types.AuthCredential.expiry
