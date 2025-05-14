from pydantic import BaseModel
from gallery import types


class ApiKeyScopeAdminUpdate(BaseModel):
    pass


class ApiKeyScopeAdminCreate(BaseModel):
    api_key_id: types.ApiKeyScope.api_key_id
    scope_id: types.ApiKeyScope.scope_id
