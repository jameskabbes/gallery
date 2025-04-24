from sqlmodel import select
from ..models.tables import ApiKey as ApiKeyTable
from . import base
from .. import types

from ..schemas import api_key as api_key_schema
from ..services import auth_credential as auth_credential_service
from .. import utils
import datetime as datetime_module


class ApiKey(
        base.Service[
            ApiKeyTable,
            types.ApiKey.id,
            api_key_schema.ApiKeyAdminCreate,
            api_key_schema.ApiKeyAdminUpdate,
        ],
        auth_credential_service.JwtIO[ApiKeyTable, types.ApiKey.id,
                                      api_key_schema.ApiKeyAdminCreate,],
        auth_credential_service.Table[ApiKeyTable,  types.ApiKey.id, api_key_schema.ApiKeyAdminCreate, ]):

    auth_type = 'api_key'
    _TABLE = ApiKeyTable

    @classmethod
    def table_id(cls, inst: ApiKeyTable):
        return inst.id

    @classmethod
    def _table_sub(cls, inst):
        return inst.id

    @classmethod
    def _build_select_by_id(cls, id):
        return select(cls._TABLE).where(cls._TABLE.id == id)

    @classmethod
    def to_api_key_private(cls, api_key: ApiKeyTable) -> api_key_schema.ApiKeyPrivate:
        return api_key_schema.ApiKeyPrivate.model_construct(**api_key.model_dump(), scope_ids=[api_key_scope.scope_id for api_key_scope in api_key.api_key_scopes])

    @classmethod
    async def table_inst_from_create_model(cls, create_model):

        return cls._TABLE(
            id=utils.generate_uuid(),
            issued=datetime_module.datetime.now().astimezone(datetime_module.UTC),
            **create_model.model_dump()
        )

    # async def get_scope_ids(self, session: Session = None, c: client.Client = None) -> list[types.ScopeTypes.id]:
    #     return [api_key_scope.scope_id for api_key_scope in self.api_key_scopes]

    # @classmethod
    # async def is_available(cls, session: Session, api_key_available_admin: ApiKeyAdminAvailable) -> bool:
    #     return not session.exec(select(cls).where(cls._build_conditions(api_key_available_admin.model_dump()))).one_or_none()

    # @classmethod
    # async def api_get_is_available(cls, session: Session, api_key_available_admin: ApiKeyAdminAvailable) -> None:

    #     if not await cls.is_available(session, api_key_available_admin):
    #         raise HTTPException(
    #             status_code=status.HTTP_409_CONFLICT, detail=cls.already_exists_message())

    # @classmethod
    # async def _check_authorization_new(cls, params):
    #     if not params.admin:
    #         if params.authorized_user_id != params.create_model.user_id:
    #             raise HTTPException(
    #                 status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to post api key for another user')

    # async def _check_authorization_existing(self, params):
    #     if not params.admin:
    #         if self.user_id != params.authorized_user_id:
    #             raise self.not_found_exception()

    # @classmethod
    # async def _check_validation_post(cls, params):
    #     await cls.api_get_is_available(params.session, ApiKeyAdminAvailable(
    #         name=params.create_model.name, user_id=params.create_model.user_id)
    #     )

    # async def _check_validation_patch(self, params):
    #     if 'name' in params.update_model.model_fields_set:
    #         await self.api_get_is_available(params.session, ApiKeyAdminAvailable(
    #             name=params.update_model.name, user_id=params.authorized_user_id))
