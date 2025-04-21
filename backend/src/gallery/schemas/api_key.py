from pydantic import BaseModel
from typing import Optional

from .. import types
from ..schemas import auth_credential


class ApiKeyAvailable(BaseModel):
    name: types.ApiKey.name


class ApiKeyAdminAvailable(ApiKeyAvailable):
    user_id: types.User.id


class ApiKeyImport(auth_credential.Import):
    pass


class ApiKeyUpdate(ApiKeyImport, auth_credential.Update):
    name: Optional[types.ApiKey.name] = None


class ApiKeyAdminUpdate(ApiKeyUpdate):
    pass


class ApiKeyCreate(ApiKeyImport, auth_credential.Create):
    name: types.ApiKey.name


class ApiKeyAdminCreate(ApiKeyCreate):
    user_id: types.User.id


class JwtPayload(auth_credential.JwtPayload):
    sub: types.User.id


class JwtModel(auth_credential.JwtModel):
    id: types.User.id
