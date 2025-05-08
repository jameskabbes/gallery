from pydantic import BaseModel
from . import auth_credential as auth_credential_schema
from .. import types
from ..schemas import FromAttributes


class UserAccessTokenAdminUpdate(BaseModel):
    expiry: types.AuthCredential.expiry


class UserAccessTokenAdminCreate(BaseModel):
    expiry: types.AuthCredential.expiry
    user_id: types.User.id


class UserAccessTokenExport(FromAttributes):
    pass


class UserAccessTokenPublic(UserAccessTokenExport):
    id: types.UserAccessToken.id
    expiry: types.AuthCredential.expiry
