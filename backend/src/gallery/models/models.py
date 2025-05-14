from sqlmodel import Field

from src.gallery.models.bases.auth_credential import AuthCredentialBase
from src.gallery import types


class SignUp(AuthCredentialBase):
    email: types.User.email = Field()
