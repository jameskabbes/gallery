import datetime as datetime_module

from backend.src.gallery.schemas.auth_credential import JwtPayload
from ..schemas import sign_up as sign_up_schema
from ..services import auth_credential as auth_credential_service
from .. import types


class SignUp(
    auth_credential_service.JwtIO[
        sign_up_schema.SignUp, types.SignUp.email, sign_up_schema.SignUpAdminCreate],
    auth_credential_service.JwtNotTable[
        sign_up_schema.SignUp, types.SignUp.email]
):

    auth_type = 'sign_up'
    _TABLE = sign_up_schema.SignUp

    @classmethod
    def _table_sub(cls, inst):
        return inst.email

    @classmethod
    async def table_inst_from_create_model(cls, create_model):
        """Create a new instance of the model from the create model (TCreateModel), don't overwrite this method"""

        return cls._TABLE(
            issued=datetime_module.datetime.now().astimezone(datetime_module.UTC),
            **create_model.model_dump()
        )

    @classmethod
    def table_inst_from_jwt_payload(cls, payload):
        return cls._TABLE(
            issued=datetime_module.datetime.fromtimestamp(payload['iat']),
            expiry=datetime_module.datetime.fromtimestamp(payload['exp']),
            email=payload['sub'],
        )
