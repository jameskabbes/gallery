from .bases.auth_credential import AuthCredentialBase
from sqlmodel import Field
from .. import types


class SignUp(AuthCredentialBase):
    email: types.User.email = Field()
