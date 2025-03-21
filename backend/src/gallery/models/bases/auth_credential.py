from pydantic import BaseModel, model_validator, field_serializer, field_validator, ValidationInfo
from sqlmodel import Field, SQLModel
import datetime as datetime_module
from gallery import types
from gallery.models.bases import jwtio
from gallery.models.bases.table import Table as BaseTable
from gallery.models import user
from gallery.models.custom_field_types.timestamp import validate_and_normalize_datetime
from sqlalchemy import Column
from gallery.models.custom_field_types import timestamp
from typing import Optional, TypedDict, ClassVar


class Import(BaseModel):
    expiry: types.AuthCredential.expiry


class Update(Import):
    pass


class Create(Import):
    pass


class JwtPayloadBase(jwtio.Payload):
    exp: types.AuthCredential.expiry_timestamp
    iat: types.AuthCredential.issued_timestamp
    type: types.AuthCredential.type


class JwtModelBase(jwtio.Model):
    expiry: types.AuthCredential.expiry_timestamp
    issued: types.AuthCredential.issued_timestamp
    type: types.AuthCredential.type


CLAIMS_MAPPING_BASE: dict[str, str] = {
    'exp': 'expiry',
    'iat': 'issued',
    'type': 'auth_type',
}


class JwtIO[TPayload: JwtPayloadBase, TModel: JwtModelBase](jwtio.JwtIO[TPayload, TModel]):
    _TYPE_CLAIM: ClassVar[str] = 'type'


class Model(SQLModel):

    # repeated in child classes due to behavior of sqlalchemy with custom type
    issued: types.AuthCredential.issued = Field(const=True)
    expiry: types.AuthCredential.expiry = Field()
    auth_type: ClassVar[types.AuthCredential.type]

    @field_validator('issued', 'expiry')
    @classmethod
    def validate_datetime(cls, value: datetime_module.datetime, info: ValidationInfo) -> datetime_module.datetime:
        return validate_and_normalize_datetime(value, info)

    @field_serializer('issued', 'expiry')
    def serialize_datetime(self, value: types.AuthCredential.issued | types.AuthCredential.expiry) -> datetime_module.datetime:
        return value.replace(tzinfo=datetime_module.timezone.utc)


class Table(SQLModel):

    user_id: types.User.id = Field(
        index=True, foreign_key=str(user.User.__tablename__) + '.' + user.ID_COL, const=True, ondelete='CASCADE')

    # @classmethod
    # async def create(cls, params: ApiPostParams['AuthCredential.Create', BaseModel]) -> typing.Self:

    #     return cls(
    #         id=cls.generate_id(),
    #         issued=datetime_module.datetime.now(
    #             datetime_module.timezone.utc),
    #         expiry=params.create_model.get_expiry(),
    #         **params.create_model.model_dump(exclude=['lifespan', 'expiry'])
    #     )

    # @classmethod
    # async def get_scope_ids(cls, session: Session = None) -> list[types.ScopeTypes.id]:
    #     return []


'''

class AuthCredential:

    class Import(BaseModel):
        lifespan: typing.Optional[AuthCredentialTypes.lifespan] = None
        expiry: typing.Optional[AuthCredentialTypes.expiry] = None

    class Create(Import):
        @model_validator(mode='after')
        def check_lifespan_or_expiry(self):
            if self.lifespan == None and self.expiry == None:
                raise ValueError(
                    "Either 'lifespan' or 'expiry' must be set and not None.")
            return self

        def get_expiry(self) -> datetime_module.datetime:
            if self.expiry != None:
                return self.expiry
            return datetime_module.datetime.now(
                datetime_module.UTC) + self.lifespan

    class Update(Import):
        pass

    class JwtEncodeBase(typing.TypedDict):
        exp: AuthCredentialTypes.expiry_timestamp
        iat: AuthCredentialTypes.issued_timestamp
        type: AuthCredentialTypes.type

    class JwtDecodeBase(typing.TypedDict):
        expiry: AuthCredentialTypes.expiry_timestamp
        issued: AuthCredentialTypes.issued_timestamp
        type: AuthCredentialTypes.type

    class JwtIO[TEncode: dict, TDecode: dict](JwtIO[TEncode, TDecode]):
        _TYPE_CLAIM: typing.ClassVar[str] = 'type'

    class Model(JwtIO):

        # repeated in child classes due to behavior of sqlalchemy with custom type
        issued: AuthCredentialTypes.issued = Field(
            const=True, sa_column=Column(DateTimeWithTimeZoneString))
        expiry: AuthCredentialTypes.expiry = Field(
            sa_column=Column(DateTimeWithTimeZoneString))
        auth_type: typing.ClassVar[AuthCredentialTypes.type]

        _JWT_CLAIMS_MAPPING_BASE: typing.ClassVar[dict[str, str]] = {
            'exp': 'expiry',
            'iat': 'issued',
            'type': 'auth_type',
        }

        @field_validator('issued', 'expiry')
        @classmethod
        def validate_datetime(cls, value: datetime_module.datetime, info: ValidationInfo) -> datetime_module.datetime:
            return validate_and_normalize_datetime(value, info)

        @field_serializer('issued', 'expiry')
        def serialize_datetime(value: datetime_module.datetime) -> datetime_module.datetime:
            return value.replace(tzinfo=datetime_module.timezone.utc)

    class Table(Table):

        user_id: types.User.id = Field(
            index=True, foreign_key=User.__tablename__ + '.' + User.ID_COLS[0], const=True, ondelete='CASCADE')

        @classmethod
        async def create(cls, params: ApiPostParams['AuthCredential.Create', BaseModel]) -> typing.Self:

            return cls(
                id=cls.generate_id(),
                issued=datetime_module.datetime.now(
                    datetime_module.timezone.utc),
                expiry=params.create_model.get_expiry(),
                **params.create_model.model_dump(exclude=['lifespan', 'expiry'])
            )

        @classmethod
        async def get_scope_ids(cls, session: Session = None) -> list[types.ScopeTypes.id]:
            return []

'''
