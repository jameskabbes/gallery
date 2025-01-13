from fastapi import HTTPException, status
import typing

AUTH_LOGOUT_HEADER = 'x-auth-logout'


class BearerCookieExceptionKwargs(typing.TypedDict):
    logout: bool = True


BearerCookieExceptionReturn = HTTPException


def make_bearer_cookie_exception(status_code: int, detail: str):
    def decorator(func):
        def wrapper(**kwargs: typing.Unpack[BearerCookieExceptionKwargs]) -> BearerCookieExceptionReturn:
            headers = {"WWW-Authenticate": "Bearer, Cookie"}
            if kwargs.get('logout', True):
                headers[AUTH_LOGOUT_HEADER] = 'true'
            return HTTPException(
                status_code=status_code,
                detail=detail,
                headers=headers
            )
        return wrapper
    return decorator


@make_bearer_cookie_exception(status.HTTP_400_BAD_REQUEST, "Improper formatting of authorization header or cookie")
def improper_format_exception():
    pass


@make_bearer_cookie_exception(status.HTTP_401_UNAUTHORIZED, "Missing required claims")
def missing_required_claims_exception():
    pass


@make_bearer_cookie_exception(status.HTTP_401_UNAUTHORIZED, "Authorization expired")
def authorization_expired_exception():
    pass


@make_bearer_cookie_exception(status.HTTP_404_NOT_FOUND, "User not found")
def user_not_found_exception():
    pass


@make_bearer_cookie_exception(status.HTTP_403_FORBIDDEN, "Authorization lacks required permissions")
def not_permitted_exception():
    pass


@make_bearer_cookie_exception(status.HTTP_401_UNAUTHORIZED, "Incorrect username or password")
def credentials_exception():
    pass


@make_bearer_cookie_exception(status.HTTP_401_UNAUTHORIZED, "Invalid OTP")
def invalid_otp_exception():
    pass


@make_bearer_cookie_exception(status.HTTP_400_BAD_REQUEST, "Invalid authorization type")
def invalid_authorization_type_exception():
    pass


type EXCEPTION = typing.Literal[
    'improper_format',
    'missing_required_claims',
    'authorization_expired',
    'user_not_found',
    'not_permitted',
    'credentials',
    'invalid_authorization_type',
    'invalid_otp'
]

EXCEPTION_MAPPING: dict[str, HTTPException] = {
    'improper_format': improper_format_exception,
    'missing_required_claims': missing_required_claims_exception,
    'authorization_expired': authorization_expired_exception,
    'user_not_found': user_not_found_exception,
    'not_permitted': not_permitted_exception,
    'credentials': credentials_exception,
    'invalid_authorization_type': invalid_authorization_type_exception,
    'invalid_otp': invalid_otp_exception
}

# Scopes
