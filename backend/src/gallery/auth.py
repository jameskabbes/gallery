from fastapi import HTTPException, status
import typing
import jwt
import datetime
from gallery import models
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'


type TokenAuthSource = typing.Literal[
    'password',
    'google_oauth2',
    'magic_link',
    'verified_magic_link',
    'sign_up'
]
TOKEN_AUTH_SOURCES: set[TokenAuthSource] = {
    'password', 'google_oauth2', 'magic_link', 'verified_magic_link', 'sign_up'}

type APIKey = str
type BearerString = Token | APIKey
type BearerType = typing.Literal['token', 'api_key']
BEARER_TYPES: set[BearerType] = {'token', 'api_key'}


def _bearer_exception(status_code: int, detail: str) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"})


def invalid_exception(detail: str) -> HTTPException:
    return _bearer_exception(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail)


def invalid_bearer_exception() -> HTTPException:
    return invalid_exception("Invalid bearer")


def invalid_token_exception() -> HTTPException:
    return invalid_exception("Invalid token")


def invalid_api_key_exception() -> HTTPException:
    return invalid_exception("Invalid API key")


def invalid_bearer_type_exception(given_bearer_type: BearerType | None = None, permitted_bearer_types: set[BearerType] | None = None) -> HTTPException:

    if given_bearer_type is not None and permitted_bearer_types is not None:
        return _bearer_exception(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer type. {given} not in {permitted}".format(
                given=given_bearer_type, permitted=permitted_bearer_types
            ))
    else:
        return _bearer_exception(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer type")


def missing_required_claims_exception() -> HTTPException:
    return _bearer_exception(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing required claims")


def bearer_expired_exception() -> HTTPException:
    return _bearer_exception(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Bearer expired")


def user_not_found_exception() -> HTTPException:
    return _bearer_exception(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found")


def user_not_permitted_exception() -> HTTPException:
    return _bearer_exception(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User does not have required permissions")


def credentials_exception() -> HTTPException:
    return _bearer_exception(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password")


def insufficient_scope_exception() -> HTTPException:
    return _bearer_exception(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="API Key has insufficient scope")


type EXCEPTION = typing.Literal[
    'invalid_bearer',
    'invalid_token',
    'invalid_api_key',
    'invalid_bearer_type',
    'missing_required_claims',
    'bearer_expired',
    'user_not_found',
    'user_not_permitted',
    'credentials',
    'insufficient_scope'
]

EXCEPTION_MAPPING: dict[EXCEPTION, HTTPException] = {
    'bearer_expired': bearer_expired_exception(),
    'credentials': credentials_exception(),
    'insufficient_scope': insufficient_scope_exception(),
    'invalid_api_key': invalid_api_key_exception(),
    'invalid_bearer': invalid_bearer_exception(),
    'invalid_bearer_type': invalid_bearer_type_exception(),
    'invalid_token': invalid_token_exception(),
    'missing_required_claims': missing_required_claims_exception(),
    'user_not_found': user_not_found_exception(),
    'user_not_permitted': user_not_permitted_exception(),
}
