from pydantic import BaseModel, field_serializer, field_validator, ValidationInfo
from typing import TypedDict, Protocol
from .. import types


class Import(BaseModel):
    expiry: types.AuthCredential.expiry


class Update(Import):
    pass


class Create(Import):
    pass


class Export(BaseModel):
    pass


class JwtModel(TypedDict):
    expiry: types.AuthCredential.expiry_timestamp
    issued: types.AuthCredential.issued_timestamp
    type: types.AuthCredential.type


class JwtPayload(TypedDict):
    exp: types.AuthCredential.expiry_timestamp
    iat: types.AuthCredential.issued_timestamp
    type: types.AuthCredential.type
