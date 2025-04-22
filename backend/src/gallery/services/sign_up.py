

from ..schemas import sign_up as sign_up_schema
from ..services import auth_credential as auth_credential_service


class SignUp(
    auth_credential_service.JwtIO[
        sign_up_schema.SignUp, sign_up_schema.SignUpAdminCreate, sign_up_schema.JwtPayload, sign_up_schema.JwtModel],

):
    _CLAIMS_MAPPING = {
        **auth_credential_service.CLAIMS_MAPPING_BASE, **{'sub': 'email'}
    }

    _TABLE = sign_up_schema.SignUp
    auth_type = 'sign_up'


#     @classmethod
#     def create(cls, create_model: SignUpAdminCreate) -> Self:
#         return cls(
#             issued=datetime_module.datetime.now(datetime_module.timezone.utc),
#             **create_model.model_dump()
#         )
