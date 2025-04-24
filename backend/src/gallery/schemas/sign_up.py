from sqlmodel import Field
from pydantic import BaseModel
from .. import types
from ..models.tables import _AuthCredentialModelBase


class SignUpAdminCreate(BaseModel):
    email: types.SignUp.email
    expiry: types.AuthCredential.expiry


class SignUp(_AuthCredentialModelBase):
    email: types.User.email = Field()
