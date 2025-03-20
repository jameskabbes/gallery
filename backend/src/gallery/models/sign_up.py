from sqlmodel import Field, Relationship, select
from typing import TYPE_CHECKING, TypedDict, Optional
from gallery import types, utils
from gallery.models.bases import auth_credential


class JwtPayload(auth_credential.JwtPayloadBase):
    sub: types.User.email


class JwtModel(auth_credential.JwtModelBase):
    email: types.User.email


class SignUpAdminCreate(auth_credential.Create):
    email: types.User.email


class SignUp(
    auth_credential.JwtIO[JwtPayload, JwtModel],
    auth_credential.Model,
):
    auth_type = 'sign_up'
    email: types.User.email = Field()
    # issued: auth_credentialTypes.issued = Field(
    #     const=True, sa_column=Column(DateTimeWithTimeZoneString))
    # expiry: auth_credentialTypes.expiry = Field(
    #     sa_column=Column(DateTimeWithTimeZoneString))

    _CLAIMS_MAPPING = {
        **auth_credential.CLAIMS_MAPPING_BASE, **{'sub': 'email'}
    }

    # @classmethod
    # def create(cls, create_model: SignUpAdminCreate) -> typing.Self:
    #     return cls(
    #         issued=datetime_module.datetime.now(
    #             datetime_module.timezone.utc),
    #         expiry=create_model.get_expiry(),
    #         **create_model.model_dump(exclude=['lifespan', 'expiry'])
    #     )


'''
# SignUp


class SignUpJwt:
    class Encode(AuthCredential.JwtEncodeBase):
        sub: types.User.email

    class Decode(AuthCredential.JwtDecodeBase):
        email: types.User.email


class SignUpAdminCreate(AuthCredential.Create):
    email: types.User.email


class SignUp(
    AuthCredential.JwtIO[SignUpJwt.Encode, SignUpJwt.Decode],
    AuthCredential.Model,
):
    auth_type = 'sign_up'
    email: types.User.email = Field()
    issued: AuthCredentialTypes.issued = Field(
        const=True, sa_column=Column(DateTimeWithTimeZoneString))
    expiry: AuthCredentialTypes.expiry = Field(
        sa_column=Column(DateTimeWithTimeZoneString))

    _JWT_CLAIMS_MAPPING = {
        **AuthCredential.Model._JWT_CLAIMS_MAPPING_BASE, **{'sub': 'email'}}

    @classmethod
    def create(cls, create_model: SignUpAdminCreate) -> typing.Self:
        return cls(
            issued=datetime_module.datetime.now(
                datetime_module.timezone.utc),
            expiry=create_model.get_expiry(),
            **create_model.model_dump(exclude=['lifespan', 'expiry'])
        )
'''
