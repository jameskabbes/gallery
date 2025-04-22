from pydantic import BaseModel, model_validator, field_serializer, field_validator, ValidationInfo
from sqlmodel import Field, SQLModel
import datetime as datetime_module
from sqlalchemy import Column
from typing import Optional, TypedDict, ClassVar, cast, Self, Literal, Protocol
from sqlmodel.ext.asyncio.session import AsyncSession
from .. import types, client

from typing import ClassVar, TypedDict, cast, TypeVar, Generic, Type
from collections.abc import Collection

from ..schemas import auth_credential as auth_credential_schemas
from ..models.bases import auth_credential as auth_credential_model
from ..models.tables import User
from . import base
from .. import utils


def lifespan_to_expiry(lifespan: datetime_module.timedelta) -> types.AuthCredential.expiry:
    return datetime_module.datetime.now(datetime_module.timezone.utc) + lifespan


CLAIMS_MAPPING_BASE = {
    'exp': 'expiry',
    'iat': 'issued',
    'type': 'auth_type',
}


TAuthCredential = TypeVar(
    'TAuthCredential', bound=auth_credential_model.AuthCredentialBase)
TCreate = TypeVar('TCreate', bound=auth_credential_schemas.Create)
TPayload = TypeVar('TPayload', bound=auth_credential_schemas.JwtPayload)
TModel = TypeVar('TModel', bound=auth_credential_schemas.JwtModel)


class MissingRequiredClaimsError(Exception):
    def __init__(self, claims: set[str]) -> None:
        super().__init__(f"Missing required claims: {', '.join(claims)}")
        self.claims = claims


class HasAuthType(Protocol):
    auth_type: ClassVar[types.AuthCredential.type]


class Model(Generic[TAuthCredential, TCreate], HasAuthType, base.HasTableInstFromCreateModel[TAuthCredential, TCreate]):
    pass


class HasUser(Protocol):
    user: User


class Table(Generic[TAuthCredential, TCreate], Model[TAuthCredential, TCreate], HasUser):
    @classmethod
    async def get_scope_ids(cls, inst: TAuthCredential | None = None, session: AsyncSession | None = None, c: client.Client | None = None) -> list[types.Scope.id]:
        return []


class JwtIO(Generic[TAuthCredential, TCreate, TPayload, TModel], Model[TAuthCredential, TCreate]):
    _TYPE_CLAIM: ClassVar[str] = 'type'
    _CLAIMS_MAPPING: ClassVar[dict[str, str]] = CLAIMS_MAPPING_BASE

    @classmethod
    def validate_jwt_claims(cls, payload: TPayload):

        missing_claims = {
            claim for claim in cls._CLAIMS_MAPPING if claim not in payload}

        print(missing_claims)

        if missing_claims:
            raise MissingRequiredClaimsError(missing_claims)

    @classmethod
    def from_payload(cls, payload: TPayload) -> TAuthCredential:

        cls.validate_jwt_claims(payload)

        converted_claims_payload = cast(TModel, {cls._CLAIMS_MAPPING[claim]: payload[claim] for claim in cls._CLAIMS_MAPPING}
                                        )

        # Create a new dictionary excluding certain keys
        new_dict = {k: v for k, v in converted_claims_payload.items() if k not in {
            'issued', 'expiry', 'auth_type'}}

        return cls._TABLE(
            **new_dict,
            issued=datetime_module.datetime.fromtimestamp(
                converted_claims_payload['issued'], datetime_module.timezone.utc),
            expiry=datetime_module.datetime.fromtimestamp(
                converted_claims_payload['expiry'], datetime_module.timezone.utc)
        )

    @classmethod
    def to_payload(cls, inst: TAuthCredential) -> TPayload:

        payload = inst.model_dump(
            include=set(cls._CLAIMS_MAPPING.values()))
        payload[cls._CLAIMS_MAPPING[cls._TYPE_CLAIM]] = cls.auth_type

        return cast(TPayload, {claim: payload[cls._CLAIMS_MAPPING[claim]] for claim in cls._CLAIMS_MAPPING.keys()})
