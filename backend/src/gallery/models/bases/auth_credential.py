from sqlmodel import SQLModel
from pydantic import field_serializer, field_validator, ValidationInfo
import datetime as datetime_module
from ... import types
from ..custom_field_types import timestamp


class AuthCredentialBase(SQLModel):
    issued: types.AuthCredential.issued
    expiry: types.AuthCredential.expiry

    @field_validator('expiry', 'issued')
    def validate_datetime(cls, v: types.AuthCredential.expiry | types.AuthCredential.issued, info: ValidationInfo) -> types.AuthCredential.expiry | types.AuthCredential.issued:
        return timestamp.validate_and_normalize_datetime(v, info)

    @field_serializer('expiry', 'issued')
    def serialize_datetime(cls, v: types.AuthCredential.expiry_timestamp | types.AuthCredential.issued_timestamp) -> types.AuthCredential.expiry | types.AuthCredential.issued:
        return datetime_module.datetime.fromtimestamp(v).astimezone(datetime_module.timezone.utc)
