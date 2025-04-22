from pydantic import BaseModel
from . import auth_credential as auth_credential_schema
from .. import types


class UserAccessTokenAdminUpdate(BaseModel):
    pass


class UserAccessTokenAdminCreate(auth_credential_schema.Create):
    user_id: types.User.id


class JwtPayload(auth_credential_schema.JwtPayload):
    sub: types.User.id


class JwtModel(auth_credential_schema.JwtModel):
    id: types.User.id


class UserAccessTokenPublic(BaseModel):
    id: types.User.id
    expiry: types.AuthCredential.expiry
