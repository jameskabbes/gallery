from sqlmodel import Field, Relationship, SQLModel, PrimaryKeyConstraint, Column
from pydantic import BaseModel, model_validator, field_serializer, field_validator, ValidationInfo
from ... import types
from typing import ClassVar, Optional
from ..custom_field_types import timestamp
import datetime as datetime_module


class Model(SQLModel):

    # repeated in child classes due to behavior of sqlalchemy with custom type
    issued: types.AuthCredential.issued = Field(
        const=True, sa_column=Column(timestamp.Timestamp))
    expiry: types.AuthCredential.expiry = Field(
        sa_column=Column(timestamp.Timestamp))
    auth_type: ClassVar[types.AuthCredential.type]

    @field_validator('issued', 'expiry')
    @classmethod
    def validate_datetime(cls, value: datetime_module.datetime, info: ValidationInfo) -> datetime_module.datetime:
        return timestamp.validate_and_normalize_datetime(value, info)

    @field_serializer('issued', 'expiry')
    def serialize_datetime(self, value: types.AuthCredential.issued | types.AuthCredential.expiry) -> datetime_module.datetime:
        return value.replace(tzinfo=datetime_module.timezone.utc)
