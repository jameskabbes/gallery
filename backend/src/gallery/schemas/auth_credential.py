from sqlmodel import SQLModel
from typing import TypedDict, Generic, TypeVar
from .. import types


# class JwtModel(TypedDict):
#     expiry: types.AuthCredential.expiry_timestamp
#     issued: types.AuthCredential.issued_timestamp
#     type: types.AuthCredential.type


class JwtPayload[TSub](TypedDict):
    sub: TSub
    exp: types.AuthCredential.expiry_timestamp
    iat: types.AuthCredential.issued_timestamp
    type: types.AuthCredential.type
