from sqlmodel import Field

from gallery.models.bases.auth_credential import AuthCredentialBase
from gallery import types


class SignUp(AuthCredentialBase):
    email: types.User.email = Field()
