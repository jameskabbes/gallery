from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from ..models.tables import ApiKey as ApiKeyTable
from . import base
from .. import types

from ..schemas import api_key as api_key_schema, auth_credential as auth_credential_schema
from ..services import auth_credential as auth_credential_service
from .. import utils, client
import datetime as datetime_module


class ApiKey(
        base.Service[
            ApiKeyTable,
            types.ApiKey.id,
            api_key_schema.ApiKeyAdminCreate,
            api_key_schema.ApiKeyAdminUpdate,
            types.ApiKey.order_by
        ],
        base.SimpleIdModelService[ApiKeyTable, types.ApiKey.id],
        auth_credential_service.JwtIO[ApiKeyTable, types.ApiKey.id],
        auth_credential_service.Table[ApiKeyTable],
        auth_credential_service.JwtAndSimpleIdTable[ApiKeyTable,
                                                    types.ApiKey.id],
):

    auth_type = auth_credential_schema.Type.API_KEY
    _MODEL = ApiKeyTable

    @classmethod
    def model_inst_from_create_model(cls, create_model):

        return cls._MODEL(
            id=types.ApiKey.id(utils.generate_uuid()),
            issued=datetime_module.datetime.now().astimezone(datetime_module.UTC),
            **create_model.model_dump()
        )

    @classmethod
    async def get_scope_ids(cls, session, c, inst):
        return [api_key_scope.scope_id for api_key_scope in inst.api_key_scopes]

    @classmethod
    async def is_available(cls, session: AsyncSession, api_key_available_admin: api_key_schema.ApiKeyAdminAvailable) -> bool:
        return (await session.exec(select(cls).where(
            api_key_schema.ApiKeyAdminAvailable.name == api_key_available_admin.name,
            api_key_schema.ApiKeyAdminAvailable.user_id == api_key_available_admin.user_id
        ))).one_or_none() is not None

    @classmethod
    async def _check_authorization_new(cls, params):
        if not params['admin']:
            if params['authorized_user_id'] != params['create_model'].user_id:
                raise base.UnauthorizedError(
                    'Unauthorized to post API Key for another user'
                )

    @classmethod
    async def _check_authorization_existing(cls, params):

        if not params['admin']:
            if params['model_inst'].user_id != params['authorized_user_id']:
                raise base.NotFoundError(
                    ApiKeyTable, params['id']
                )

    # @classmethod
    # async def _check_validation_post(cls, params):
    #     await cls.api_get_is_available(params.session, ApiKeyAdminAvailable(
    #         name=params.create_model.name, user_id=params.create_model.user_id)
    #     )

    # async def _check_validation_patch(self, params):
    #     if 'name' in params.update_model.model_fields_set:
    #         await self.api_get_is_available(params.session, ApiKeyAdminAvailable(
    #             name=params.update_model.name, user_id=params.authorized_user_id))
