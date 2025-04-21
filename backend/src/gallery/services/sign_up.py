from sqlmodel import Field, Relationship, select
from typing import TYPE_CHECKING, TypedDict, Optional, Self
import datetime as datetime_module

from .. import types, utils
from .bases import auth_credential


class JwtPayload(auth_credential.JwtPayload):
    sub: types.User.email


class JwtModel(auth_credential.JwtModel):
    email: types.User.email


class SignUpAdminCreate(auth_credential.Create):
    email: types.User.email


# class SignUp(
#     auth_credential.JwtIO[JwtPayload, JwtModel],
# ):
#     auth_type = 'sign_up'
#     email: types.User.email = Field()

#     _CLAIMS_MAPPING = {
#         **auth_credential.CLAIMS_MAPPING_BASE, **{'sub': 'email'}
#     }

#     @classmethod
#     def create(cls, create_model: SignUpAdminCreate) -> Self:
#         return cls(
#             issued=datetime_module.datetime.now(datetime_module.timezone.utc),
#             **create_model.model_dump()
#         )
