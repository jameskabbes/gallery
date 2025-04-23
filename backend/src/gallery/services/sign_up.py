from ..schemas import sign_up as sign_up_schema
from ..services import auth_credential as auth_credential_service
import datetime as datetime_module


class SignUp(
    auth_credential_service.JwtIO[
        sign_up_schema.SignUp, sign_up_schema.SignUpAdminCreate, sign_up_schema.JwtPayload, sign_up_schema.JwtModel],

):
    _CLAIMS_MAPPING = {
        **auth_credential_service.CLAIMS_MAPPING_BASE, **{'sub': 'email'}
    }

    _TABLE = sign_up_schema.SignUp
    auth_type = 'sign_up'

    @classmethod
    async def table_inst_from_create_model(cls, create_model):
        """Create a new instance of the model from the create model (TCreateModel), don't overwrite this method"""

        return cls._TABLE(
            issued=datetime_module.datetime.now().astimezone(datetime_module.UTC),
            **create_model.model_dump()
        )
