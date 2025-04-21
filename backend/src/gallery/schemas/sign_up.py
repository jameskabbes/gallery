from pydantic import Field
from .. import types
from .auth import AuthCredential


class SignUp(AuthCredential):
    auth_type = 'sign_up'
    email: types.User.email = Field()
