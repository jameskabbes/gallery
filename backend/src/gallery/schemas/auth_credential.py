from pydantic import BaseModel
from typing import TypedDict
from .. import types


class Import(BaseModel):
    expiry: types.AuthCredential.expiry


class Update(Import):
    pass


class Create(Import):
    pass


class JwtModel(TypedDict):
    expiry: types.AuthCredential.expiry_timestamp
    issued: types.AuthCredential.issued_timestamp
    type: types.AuthCredential.type


class JwtPayload(TypedDict):
    exp: types.AuthCredential.expiry_timestamp
    iat: types.AuthCredential.issued_timestamp
    type: types.AuthCredential.type
