from pydantic import BaseModel
from typing import Optional

from arbor_imago import types
from arbor_imago.schemas import auth_credential as auth_credential_schema


class ApiKeyAvailable(BaseModel):
    name: types.ApiKey.name


class ApiKeyAdminAvailable(ApiKeyAvailable):
    user_id: types.User.id


class ApiKeyImport(BaseModel):
    pass


class ApiKeyUpdate(ApiKeyImport):
    name: Optional[types.ApiKey.name] = None
    expiry: types.AuthCredential.expiry | None = None


class ApiKeyAdminUpdate(ApiKeyUpdate, BaseModel):
    pass


class ApiKeyCreate(ApiKeyImport):
    name: types.ApiKey.name
    expiry: types.AuthCredential.expiry


class ApiKeyAdminCreate(ApiKeyCreate, BaseModel):
    user_id: types.User.id


class ApiKeyExport(BaseModel):
    id: types.ApiKey.id
    user_id: types.User.id
    name: types.ApiKey.name
    issued: types.ApiKey.issued
    expiry: types.ApiKey.expiry


class ApiKeyPublic(ApiKeyExport):
    pass


class ApiKeyPrivate(ApiKeyExport):
    pass
