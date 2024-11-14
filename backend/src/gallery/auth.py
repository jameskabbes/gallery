from fastapi import HTTPException, status
import typing

AUTH_ERROR_HEADER = 'x-auth-error'


def _bearer_cookie_exception(status_code: int, detail: str) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer, Cookie", AUTH_ERROR_HEADER: 'true'})


def improper_format_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Improper formatting of authorization header or cookie",
        headers={"WWW-Authenticate": "Bearer, Cookie", AUTH_ERROR_HEADER: 'true'})


def missing_required_claims_exception() -> HTTPException:
    return _bearer_cookie_exception(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing required claims")


def authorization_expired_exception() -> HTTPException:
    return _bearer_cookie_exception(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authorization expired")


def user_not_found_exception() -> HTTPException:
    return _bearer_cookie_exception(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found")


def not_permitted_exception() -> HTTPException:
    return _bearer_cookie_exception(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Authorizaton lacks required permissions")


def credentials_exception() -> HTTPException:
    return _bearer_cookie_exception(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password")


def invalid_authorization_type_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid authorization type",
        headers={"WWW-Authenticate": "Bearer, Cookie", AUTH_ERROR_HEADER: 'true'})


type EXCEPTION = typing.Literal[
    'improper_format',
    'missing_required_claims',
    'authorization_expired',
    'user_not_found',
    'not_permitted',
    'credentials',
    'invalid_authorization_type'
]

EXCEPTION_MAPPING: dict[EXCEPTION, typing.Callable[[], HTTPException]] = {
    'improper_format': improper_format_exception,
    'missing_required_claims': missing_required_claims_exception,
    'authorization_expired': authorization_expired_exception,
    'user_not_found': user_not_found_exception,
    'not_permitted': not_permitted_exception,
    'credentials': credentials_exception,
    'invalid_authorization_type': invalid_authorization_type_exception
}

# Scopes
