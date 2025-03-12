from gallery import client, types
from gallery.config import settings
import typing
from fastapi import Request, HTTPException, status, Response
import datetime

ACCESS_TOKEN_COOKIE_KEY = "access_token"


class ExceptionKwargs(typing.TypedDict):
    logout_on_exception: bool = True


AuthExceptionFunction = typing.Callable[[bool], HTTPException]


def base_exception(status_code: int, detail: str, logout_on_exception: bool = True) -> HTTPException:
    headers = {"WWW-Authenticate": "Bearer, Cookie"}
    if logout_on_exception:
        headers[settings.SHARED_CONSTANTS['header_keys']
                ['auth_logout']] = 'true'
    return HTTPException(
        status_code=status_code,
        detail=detail,
        headers=headers
    )


def both_authorization_header_and_cookie_exception(**kwargs: typing.Unpack[ExceptionKwargs]) -> HTTPException:
    return base_exception(status_code=status.HTTP_400_BAD_REQUEST, detail="Both Bearer token in the Authorization header and {} cookie supplied, which is prohibited".format(ACCESS_TOKEN_COOKIE_KEY), **kwargs)


def missing_authorization_exception(**kwargs: typing.Unpack[ExceptionKwargs]) -> HTTPException:
    return base_exception(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header or {} cookie".format(ACCESS_TOKEN_COOKIE_KEY), **kwargs)


def improper_format_exception(**kwargs: typing.Unpack[ExceptionKwargs]) -> HTTPException:
    return base_exception(status_code=status.HTTP_400_BAD_REQUEST, detail="Improper format for authorization token", **kwargs)


def missing_required_claims_exception(**kwargs: typing.Unpack[ExceptionKwargs]) -> HTTPException:
    return base_exception(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing required claims in authorization token", **kwargs)


def authorization_expired_exception(**kwargs: typing.Unpack[ExceptionKwargs]) -> HTTPException:
    return base_exception(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization expired", **kwargs)


def user_not_found_exception(**kwargs: typing.Unpack[ExceptionKwargs]) -> HTTPException:
    return base_exception(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found", **kwargs)


def not_permitted_exception(**kwargs: typing.Unpack[ExceptionKwargs]) -> HTTPException:
    return base_exception(status_code=status.HTTP_403_FORBIDDEN, detail="Not permitted", **kwargs)


def credentials_exception(**kwargs: typing.Unpack[ExceptionKwargs]) -> HTTPException:
    return base_exception(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", **kwargs)


def invaliad_otp_exception(**kwargs: typing.Unpack[ExceptionKwargs]) -> HTTPException:
    return base_exception(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid OTP", **kwargs)


def authorization_type_not_permitted_exception(**kwargs: typing.Unpack[ExceptionKwargs]) -> HTTPException:
    return base_exception(status_code=status.HTTP_400_BAD_REQUEST, detail="Authorization type not permitted for this endpoint", **kwargs)


def set_access_token_cookie(response: Response, access_token: types.JwtEncodedStr,  lifespan: datetime.timedelta | None):

    kwargs = {}
    if lifespan:
        kwargs['expires'] = datetime.datetime.now(
            datetime.UTC) + lifespan

    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE_KEY,
        value=access_token,
        httponly=True,
        secure=True,
        samesite="Lax",
        **kwargs
    )


def delete_access_token_cookie(response: Response):
    response.delete_cookie(ACCESS_TOKEN_COOKIE_KEY)
