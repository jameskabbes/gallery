from pydantic import BaseModel, model_validator, field_serializer, field_validator, ValidationInfo
from sqlmodel import Field, SQLModel
from sqlmodel.sql.expression import SelectOfScalar
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


TAuthCredential = TypeVar(
    'TAuthCredential', bound=schemas.AuthCredentialInstance)
TAuthCredentialTable = TypeVar(
    'TAuthCredentialTable', bound=schemas.AuthCredentialTableInstance)
TAuthCredentialJwt = TypeVar(
    'TAuthCredentialJwt', bound=schemas.AuthCredentialJwtInstance)
TSub = TypeVar('TSub')


class _Base(
        Generic[TAuthCredential, TSub, base.TCreateModel],
        base.TableInstFromCreateModel[TAuthCredential, base.TCreateModel],
):
    auth_type: ClassVar[types.AuthCredential.type]

    @classmethod
    def _table_sub(cls, inst: TAuthCredential) -> TSub:
        raise NotImplementedError


class Table(
    Generic[TAuthCredentialTable],
):
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


class JwtIO(
    Generic[TAuthCredentialJwt, TSub, base.TCreateModel],
    _Base[TAuthCredentialJwt, TSub, base.TCreateModel]
):
    _CLAIMS: ClassVar[set[str]] = {'type', 'exp', 'iat', 'sub'}

    @classmethod
    def validate_jwt_claims(cls, payload: auth_credential_schema.JwtPayload[TSub]):

        missing_claims = {
            claim for claim in cls._CLAIMS if claim not in payload}
        if missing_claims:
            raise MissingRequiredClaimsError(missing_claims)

    @classmethod
    def to_jwt_payload(cls, inst: TAuthCredentialJwt) -> auth_credential_schema.JwtPayload[TSub]:

        return {
            'type': cls.auth_type,
            'exp': inst.expiry.timestamp(),
            'iat': inst.issued.timestamp(),
            'sub': cls._table_sub(inst),
        }


class JwtNotTable(
    Generic[TAuthCredentialJwt, TSub],
):

    @classmethod
    def table_inst_from_jwt_payload(
            cls,
            payload: auth_credential_schema.JwtPayload[TSub]) -> TAuthCredentialJwt:
        raise NotImplementedError
