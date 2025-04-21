from pydantic import BaseModel, model_validator, field_serializer, field_validator, ValidationInfo
from sqlmodel import Field, SQLModel
import datetime as datetime_module
from sqlalchemy import Column
from typing import Optional, TypedDict, ClassVar, cast, Self, Literal
from sqlmodel.ext.asyncio.session import AsyncSession
from .. import types

from typing import ClassVar, TypedDict, cast, TypeVar, Generic, Type
from collections.abc import Collection

from ..schemas import auth_credential as auth_credential_schemas
from ..models.bases import auth_credential as auth_credential_model


def lifespan_to_expiry(lifespan: datetime_module.timedelta) -> types.AuthCredential.expiry:
    return datetime_module.datetime.now(datetime_module.timezone.utc) + lifespan


CLAIMS_MAPPING_BASE = {
    'exp': 'expiry',
    'iat': 'issued',
    'type': 'auth_type',
}


TPayload = TypeVar('TPayload', bound=auth_credential_schemas.JwtPayload)
TModel = TypeVar('TModel', bound=auth_credential_schemas.JwtModel)


class MissingRequiredClaimsError(Exception):
    def __init__(self, claims: set[str]) -> None:
        super().__init__(f"Missing required claims: {', '.join(claims)}")
        self.claims = claims


class JwtIO(Generic[TPayload, TModel]):

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
    def from_payload(cls, payload: TPayload) -> Self:

        cls.validate_jwt_claims(payload)

        converted_claims_payload = cast(TModel, {cls._CLAIMS_MAPPING[claim]: payload[claim] for claim in cls._CLAIMS_MAPPING}
                                        )

        # Create a new dictionary excluding certain keys
        new_dict = {k: v for k, v in converted_claims_payload.items() if k not in {
            'issued', 'expiry', 'auth_type'}}

        return cls(
            **new_dict,
            issued=datetime_module.datetime.fromtimestamp(
                converted_claims_payload['issued'], datetime_module.timezone.utc),
            expiry=datetime_module.datetime.fromtimestamp(
                converted_claims_payload['expiry'], datetime_module.timezone.utc)
        )

    def to_payload(self) -> TPayload:

        payload = self.model_dump(
            include=set(self._CLAIMS_MAPPING.values()))
        payload[self._CLAIMS_MAPPING[self._TYPE_CLAIM]] = self.auth_type

        return cast(TPayload, {claim: payload[self._CLAIMS_MAPPING[claim]] for claim in self._CLAIMS_MAPPING.keys()})

    # @classmethod
    # async def create(cls, params: ApiPostParams['AuthCredential.Create', BaseModel]) -> typing.Self:

    #     return cls(
    #         id=cls.generate_id(),
    #         issued=datetime_module.datetime.now(
    #             datetime_module.timezone.utc),
    #         expiry=params.create_model.get_expiry(),
    #         **params.create_model.model_dump(exclude=['lifespan', 'expiry'])
    #     )

    @classmethod
    async def get_scope_ids(cls, session: AsyncSession | None = None) -> list[types.Scope.id]:
        return []
