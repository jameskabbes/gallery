from typing import ClassVar, TypedDict, cast, TypeVar, Generic, Type


class Payload(TypedDict):
    pass


class Model(TypedDict):
    pass


TPayload = TypeVar('TPayload', bound=Payload)
TModel = TypeVar('TModel', bound=Model)


class JwtIO(Generic[TPayload, TModel]):

    _CLAIMS_MAPPING: ClassVar[dict[str, str]] = {}

    @classmethod
    def validate_jwt_claims(cls, payload: TPayload) -> bool:
        return all(claim in payload for claim in cls._CLAIMS_MAPPING)

    @classmethod
    def decode(cls, payload: TPayload) -> TModel:
        return cast(TModel, {cls._CLAIMS_MAPPING[claim]: payload[claim] for claim in cls._CLAIMS_MAPPING})

    @classmethod
    def encode(cls, model: TModel) -> TPayload:

        encoded_payload = {}
        for claim in model.keys():
            if claim not in cls._CLAIMS_MAPPING:
                raise ValueError(f"Invalid claim key: {claim}")

            encoded_payload[cls._CLAIMS_MAPPING[claim]] = model[claim]

        return cast(TPayload, encoded_payload)
