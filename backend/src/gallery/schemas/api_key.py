from pydantic import BaseModel
from typing import Optional

from .. import types
from ..schemas import auth_credential as auth_credential_schema


class ApiKeyAvailable(BaseModel):
    name: types.ApiKey.name


class ApiKeyAdminAvailable(ApiKeyAvailable):
    user_id: types.User.id


class ApiKeyImport(auth_credential_schema.Import):
    pass


class ApiKeyUpdate(ApiKeyImport, auth_credential_schema.Update):
    name: Optional[types.ApiKey.name] = None


class ApiKeyAdminUpdate(ApiKeyUpdate):
    pass


class ApiKeyCreate(ApiKeyImport, auth_credential_schema.Create):
    name: types.ApiKey.name


class ApiKeyAdminCreate(ApiKeyCreate):
    user_id: types.User.id


class JwtPayload(auth_credential_schema.JwtPayload):
    sub: types.User.id


class JwtModel(auth_credential_schema.JwtModel):
    id: types.User.id


class ApiKeyExport(BaseModel):
    id: types.ApiKey.id
    user_id: types.User.id
    name: types.ApiKey.name
    issued: types.ApiKey.issued
    expiry: types.ApiKey.expiry


class ApiKeyPublic(ApiKeyExport):
    pass


class ApiKeyPrivate(ApiKeyExport):
    scope_ids: list[types.Scope.id]
