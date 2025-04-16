from .. import types
from . import base


class ApiKeyScopeRouter(base.Router):
    _PREFIX = '/api_key_scope'
    _TAGS = ['Api Key Scope']

    def _set_routes(self):

        @self.router.get('/')
        async def add_scope_to_api_key(
            api_key_id: types.ApiKey.id,
            scope_id: types.Scope.id,
            # authorization: Annotated[GetAuthorizationReturn, Depends(
            #     make_get_auth_dependency())]
        ):
            async with self.client.AsyncSession() as session:
                return None
                # return await models.ApiKeyScope.api_post(models.ApiKeyScope.PostParams.model_construct(session=session, c=c, authorized_user_id=authorization._user_id, create_model=models.ApiKeyScopeAdminCreate(api_key_id=api_key_id, scope_id=scope_id)))
