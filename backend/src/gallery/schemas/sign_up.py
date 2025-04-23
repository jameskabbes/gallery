from sqlmodel import Field
from pydantic import BaseModel
from ..schemas import auth_credential as auth_credential_schema
from .. import types


class JwtPayload(auth_credential_schema.JwtPayload):
    sub: types.User.email


class JwtModel(auth_credential_schema.JwtModel):
    email: types.User.email


class SignUpAdminCreate(BaseModel):
    email: types.User.email
    expiry: types.AuthCredential.expiry


class SignUp(auth_credential_schema.Model):
    email: types.User.email = Field()
