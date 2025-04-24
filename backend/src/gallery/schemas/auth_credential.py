from sqlmodel import SQLModel
from typing import TypedDict
from .. import types


class JwtModel(TypedDict):
    expiry: types.AuthCredential.expiry_timestamp
    issued: types.AuthCredential.issued_timestamp
    type: types.AuthCredential.type


class JwtPayload(TypedDict):
    exp: types.AuthCredential.expiry_timestamp
    iat: types.AuthCredential.issued_timestamp
    type: types.AuthCredential.type


class Model(SQLModel):
    issued: types.AuthCredential.issued
    expiry: types.AuthCredential.expiry
