from pydantic import BaseModel, model_validator, field_serializer, field_validator, ValidationInfo
from sqlmodel import Field, SQLModel
import datetime as datetime_module
from typing import Optional, TypedDict, ClassVar, cast, Self, Literal, Protocol
from sqlmodel.ext.asyncio.session import AsyncSession
from .. import types, client

from typing import ClassVar, TypedDict, cast, TypeVar, Generic, Type

from ..schemas import auth_credential as auth_credential_schema
from ..models.tables import User
from . import base
from .. import utils, models, schemas


def lifespan_to_expiry(lifespan: datetime_module.timedelta) -> types.AuthCredential.expiry:
    return datetime_module.datetime.now() + lifespan


CLAIMS_MAPPING_BASE = {
    'exp': 'expiry',
    'iat': 'issued',
    'type': 'auth_type',
}


TAuthCredential = TypeVar(
    'TAuthCredential', bound=schemas.AuthCredentialInstance)
TAuthCredentialTable = TypeVar(
    'TAuthCredentialTable', bound=schemas.AuthCredentialTableInstance)
TAuthCredentialJwt = TypeVar(
    'TAuthCredentialJwt', bound=schemas.AuthCredentialJwtInstance)

TAdminCreate = TypeVar(
    'TAdminCreate', bound=BaseModel)
TJwtPayload = TypeVar('TJwtPayload', bound=auth_credential_schema.JwtPayload)
TJwtModel = TypeVar('TJwtModel', bound=auth_credential_schema.JwtModel)


class _Base(Generic[TAuthCredential, TAdminCreate], base.HasTableInstFromCreateModel[TAuthCredential, TAdminCreate]):
    auth_type: ClassVar[types.AuthCredential.type]


# class Model2(SQLModel):
#     issued: types.AuthCredential.issued
#     expiry: types.AuthCredential.expiry

#     # @field_serializer('issued', 'expiry')
#     # def serialize_datetime(self, value: types.AuthCredential.issued | types.AuthCredential.expiry) -> datetime_module.datetime:
#     #     return

#     @field_validator('issued', 'expiry')
#     @classmethod
#     def validate_datetime(cls, value: datetime_module.datetime, info: ValidationInfo) -> datetime_module.datetime:
#         return timestamp.validate_and_normalize_datetime(value, info)


class Table(Generic[TAuthCredentialTable, TAdminCreate], _Base[TAuthCredentialTable, TAdminCreate]):
    @classmethod
    async def get_scope_ids(
            cls,
            inst: TAuthCredentialTable | None = None,
            session: AsyncSession | None = None,
            c: client.Client | None = None) -> list[types.Scope.id]:
        return []


class MissingRequiredClaimsError(Exception):
    def __init__(self, claims: set[str]) -> None:
        super().__init__(f"Missing required claims: {', '.join(claims)}")
        self.claims = claims


class JwtIO(Generic[TAuthCredentialJwt, TAdminCreate, TJwtPayload, TJwtModel], _Base[TAuthCredentialJwt, TAdminCreate]):
    _TYPE_CLAIM: ClassVar[str] = 'type'
    _CLAIMS_MAPPING: ClassVar[dict[str, str]] = CLAIMS_MAPPING_BASE

    @classmethod
    def validate_jwt_claims(cls, payload: TJwtPayload):

        missing_claims = {
            claim for claim in cls._CLAIMS_MAPPING if claim not in payload}
        if missing_claims:
            raise MissingRequiredClaimsError(missing_claims)

    @classmethod
    def from_jwt_payload(cls, payload: TJwtPayload) -> TAuthCredentialJwt:
        raise NotImplementedError

        cls.validate_jwt_claims(payload)

        converted_claims_payload = {
            cls._CLAIMS_MAPPING[claim]: payload[claim] for claim in cls._CLAIMS_MAPPING}

        # Create a new dictionary excluding certain keys
        new_dict: TJwtModel = {k: v for k, v in converted_claims_payload.items() if k not in {
            'issued', 'expiry', 'auth_type'}}

        return cls._TABLE(
            **new_dict,
            issued=datetime_module.datetime.fromtimestamp(
                converted_claims_payload['issued'], datetime_module.timezone.utc),
            expiry=datetime_module.datetime.fromtimestamp(
                converted_claims_payload['expiry'], datetime_module.timezone.utc)
        )

    @classmethod
    def to_jwt_payload(cls, inst: TAuthCredentialJwt) -> TJwtPayload:
        raise NotImplementedError

        payload = inst.model_dump(
            include=set(cls._CLAIMS_MAPPING.values()))
        payload[cls._CLAIMS_MAPPING[cls._TYPE_CLAIM]] = cls.auth_type

        return cast(TJwtPayload, {claim: payload[cls._CLAIMS_MAPPING[claim]] for claim in cls._CLAIMS_MAPPING.keys()})
