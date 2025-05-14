from pydantic import BaseModel
from gallery import types
from gallery.schemas import FromAttributes


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


class UserAccessTokenPrivate(UserAccessTokenExport):
    id: types.UserAccessToken.id
    expiry: types.AuthCredential.expiry
    user_id: types.User.id
