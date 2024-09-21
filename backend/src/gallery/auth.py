from fastapi import HTTPException, status
import typing


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
    'invalid_token': invalid_token_exception(),
    'missing_required_claims': missing_required_claims_exception(),
    'user_not_found': user_not_found_exception(),
    'user_not_permitted': user_not_permitted_exception(),
}
