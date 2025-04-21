from pydantic import BaseModel, Field, field_validator, field_serializer
from .. import types
from typing import ClassVar
import datetime as datetime_module
from pydantic import ValidationInfo


class AuthCredential(BaseModel):

    # repeated in child classes due to behavior of sqlalchemy with custom type
    issued: types.AuthCredential.issued = Field()
    expiry: types.AuthCredential.expiry = Field()
    auth_type: ClassVar[types.AuthCredential.type]

    @field_validator('issued', 'expiry')
    @classmethod
    def validate_datetime(cls, value: datetime_module.datetime, info: ValidationInfo) -> datetime_module.datetime:
        return timestamp.validate_and_normalize_datetime(value, info)

    @field_serializer('issued', 'expiry')
    def serialize_datetime(self, value: types.AuthCredential.issued | types.AuthCredential.expiry) -> datetime_module.datetime:
        return value.replace(tzinfo=datetime_module.timezone.utc)
