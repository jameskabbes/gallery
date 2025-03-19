from pydantic import BaseModel
from typing import ClassVar, TypedDict, Any, cast


class Payload(TypedDict):
    pass


class Model(TypedDict):
    pass


class JwtIO[TPayload: Payload, TModel: Model](BaseModel):

    _CLAIMS_MAPPING: ClassVar[dict[str, str]] = {}

    @classmethod
    def validate_jwt_claims(cls, payload: TPayload) -> bool:
        return all(claim in payload for claim in cls._CLAIMS_MAPPING)

    @classmethod
    def decode(cls, payload: TPayload) -> TModel:
        return cast(TModel, {cls._CLAIMS_MAPPING[claim]: payload[claim] for claim in cls._CLAIMS_MAPPING})

    def encode(self) -> TPayload:
        a = cast(TModel, self.model_dump(
            include=set(self._CLAIMS_MAPPING.keys())))
        return cast(TPayload, {self._CLAIMS_MAPPING[key]: value for key, value in a.items()})
