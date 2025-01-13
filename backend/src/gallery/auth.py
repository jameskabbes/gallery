from fastapi import HTTPException, status
from pydantic import BaseModel
from gallery import client
import typing


class BearerCookieExceptionKwargs(typing.TypedDict):
    logout: bool


BearerCookieExceptionReturn = HTTPException


EXCEPTION = typing.Literal[
    'improper_format',
    'both_authorization_header_and_cookie',
    'missing_required_claims',
    'authorization_expired',
    'user_not_found',
    'not_permitted',
    'credentials',
    'invalid_authorization_type',
    'invalid_otp'
]


class AuthExceptionManager(BaseModel):

    c: client.Client

    def _bearer_or_cookie_exception(self, status_code: int, detail: str, logout: bool = True) -> BearerCookieExceptionReturn:
        headers = {"WWW-Authenticate": (
            'Bearer realm="Access to the API", '
            'token_type="JWT", '
            'cookie_name="access_token", '
            'instructions="Provide a JWT as a 1) Bearer token in the Authorzation header or 2) as a cookie named {}"'.format(
                self.c.header_keys['access_token'])
        )}

        if logout:
            headers[self.c.header_keys['auth_logout']] = 'true'

        return HTTPException(
            status_code=status_code,
            detail=detail,
            headers=headers
        )

    # def make_bearer_cookie_exception(status_code: int, detail: str):
    #     def decorator(func):
    #         def wrapper(**kwargs: typing.Unpack[BearerCookieExceptionKwargs]) -> BearerCookieExceptionReturn:
    #             headers = {"WWW-Authenticate": "Bearer, Cookie"}
    #             if kwargs.get('logout', True):
    #                 headers[AUTH_LOGOUT_HEADER] = 'true'
    #             return HTTPException(
    #                 status_code=status_code,
    #                 detail=detail,
    #                 headers=headers
    #             )
    #         return wrapper
    #     return decorator

    def make_bearer_or_cookie_exception(self, status_code: int, detail: str):
        def decorator(func):
            def wrapper(**kwargs: typing.Unpack[BearerCookieExceptionKwargs]) -> BearerCookieExceptionReturn:
                return self._bearer_or_cookie_exception(status_code=status_code, detail=detail, **kwargs)
            return wrapper
        return decorator

    @make_bearer_or_cookie_exception(status_code=status.HTTP_400_BAD_REQUEST, detail="Both Bearer token in the Authorization header and access_token cookie supplied, which is prohibited")
    def both_authorization_header_and_cookie_exception():
        pass

    @make_bearer_or_cookie_exception(status_code=status.HTTP_401_UNAUTHORIZED, detail="Improper format of authorization token")
    def improper_format_exception():
        pass

    @make_bearer_or_cookie_exception(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing required claims")
    def missing_required_claims_exception():
        pass

    @make_bearer_or_cookie_exception(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization expired")
    def authorization_expired_exception():
        pass

    @make_bearer_or_cookie_exception(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    def user_not_found_exception():
        pass

    @make_bearer_or_cookie_exception(status_code=status.HTTP_403_FORBIDDEN, detail="Authorization lacks required permissions")
    def not_permitted_exception():
        pass

    @make_bearer_or_cookie_exception(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    def credentials_exception():
        pass

    @make_bearer_or_cookie_exception(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid OTP")
    def invalid_otp_exception():
        pass

    @make_bearer_or_cookie_exception(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid authorization type")
    def invalid_authorization_type_exception():
        pass

    EXCEPTION_MAPPING: dict[EXCEPTION, typing.Callable[[typing.Unpack[BearerCookieExceptionKwargs]], BearerCookieExceptionReturn]] = {
        'improper_format': improper_format_exception,
        'both_authorization_header_and_cookie': both_authorization_header_and_cookie_exception,
        'missing_required_claims': missing_required_claims_exception,
        'authorization_expired': authorization_expired_exception,
        'user_not_found': user_not_found_exception,
        'not_permitted': not_permitted_exception,
        'credentials': credentials_exception,
        'invalid_authorization_type': invalid_authorization_type_exception,
        'invalid_otp': invalid_otp_exception
    }
