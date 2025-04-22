from sqlmodel import SQLModel
from pydantic import BaseModel, field_serializer, field_validator, ValidationInfo
from typing import TypedDict, Protocol
from ... import types
import datetime as datetime_module
from ..custom_field_types import timestamp


class AuthCredentialBase(SQLModel):
    issued: types.AuthCredential.issued
    expiry: types.AuthCredential.expiry

    @field_serializer('issued', 'expiry')
    def serialize_datetime(self, value: types.AuthCredential.issued | types.AuthCredential.expiry) -> datetime_module.datetime:
        return value.replace(tzinfo=datetime_module.timezone.utc)

    @field_validator('issued', 'expiry')
    @classmethod
    def validate_datetime(cls, value: datetime_module.datetime, info: ValidationInfo) -> datetime_module.datetime:
        return timestamp.validate_and_normalize_datetime(value, info)
