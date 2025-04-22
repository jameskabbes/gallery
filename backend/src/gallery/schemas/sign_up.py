from sqlmodel import Field
from ..schemas import auth_credential as auth_credential_schema
from ..models.bases import auth_credential as auth_credential_model_base
from .. import types


class JwtPayload(auth_credential_schema.JwtPayload):
    sub: types.User.email


class JwtModel(auth_credential_schema.JwtModel):
    email: types.User.email


class SignUpAdminCreate(auth_credential_schema.Create):
    email: types.User.email


class SignUp(auth_credential_model_base.AuthCredentialBase):
    email: types.User.email = Field()
