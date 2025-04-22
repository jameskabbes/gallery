from typing import Any
from sqlmodel import select
from pydantic import BaseModel
import datetime as datetime_module

from ..models.tables import UserAccessToken as UserAccessTokenTable
from . import base
from .. import types

from ..schemas import user_access_token as user_access_token_schema
from ..services import auth_credential as auth_credential_service
from .. import utils


class UserAccessToken(
    base.Service[
        UserAccessTokenTable,
        types.UserAccessToken.id,
        user_access_token_schema.UserAccessTokenAdminCreate,
        user_access_token_schema.UserAccessTokenAdminUpdate
    ],
    auth_credential_service.JwtIO[
        UserAccessTokenTable,
        user_access_token_schema.UserAccessTokenAdminCreate,
        user_access_token_schema.JwtPayload,
        user_access_token_schema.JwtModel,
    ],
    auth_credential_service.Table[
        UserAccessTokenTable,
        user_access_token_schema.UserAccessTokenAdminCreate,
    ],
):

    _CLAIMS_MAPPING = {
        **auth_credential_service.CLAIMS_MAPPING_BASE, **{'sub': 'id'}
    }

    auth_type = 'access_token'
    _TABLE = UserAccessTokenTable

    @classmethod
    def table_id(cls, inst):
        return inst.id

    @classmethod
    def _build_select_by_id(cls, id):
        return select(cls._TABLE).where(cls._TABLE.id == id)

    @classmethod
    async def table_inst_from_create_model(cls, create_model: user_access_token_schema.UserAccessTokenAdminCreate) -> UserAccessTokenTable:

        return cls._TABLE(
            id=utils.generate_uuid(),
            issued=datetime_module.datetime.now(datetime_module.timezone.utc),
            **create_model.model_dump(exclude_unset=True, exclude_defaults=True, exclude_none=True)
        )

    # @classmethod
    # async def _check_authorization_new(cls, params):

    #     if not params.admin:
    #         if params.authorized_user_id != params.create_model.user_id:
    #             raise HTTPException(
    #                 status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to post access token for another user')

    # async def _check_authorization_existing(self, params):
    #     if not params.admin:
    #         if self.user_id != params.authorized_user_id:
    #             raise self.not_found_exception()

    # async def get_scope_ids(self, session: Session = None) -> list[types.ScopeTypes.id]:
    #     return config.USER_ROLE_ID_SCOPE_IDS[self.user.user_role_id]
