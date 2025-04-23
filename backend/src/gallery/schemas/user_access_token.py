from pydantic import BaseModel
from . import auth_credential as auth_credential_schema
from .. import types
from ..schemas import FromAttributes


class UserAccessTokenAdminUpdate(BaseModel):
    expiry: types.AuthCredential.expiry | None = None


class UserAccessTokenAdminCreate(BaseModel):
    expiry: types.AuthCredential.expiry
    user_id: types.User.id


class JwtPayload(auth_credential_schema.JwtPayload):
    sub: types.User.id


class JwtModel(auth_credential_schema.JwtModel):
    id: types.User.id


class UserAccessTokenExport(FromAttributes):
    pass


class UserAccessTokenPublic(UserAccessTokenExport):
    id: types.User.id
    expiry: types.AuthCredential.expiry
