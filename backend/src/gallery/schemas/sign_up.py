from sqlmodel import Field
from ..bases import auth_credential
from ... import types


class SignUp(auth_credential.Model):
    auth_type = 'sign_up'
    email: types.User.email = Field()
