import typing
from fastapi import Request, HTTPException, status, Response
import datetime
from .. import client, types, auth
from ..config import settings


class StatusCodeAndDetail(typing.TypedDict):
    status_code: int
    detail: str


def Base(status_code_and_detail: StatusCodeAndDetail, logout: bool = True) -> HTTPException:
    headers = {"WWW-Authenticate": "Bearer, Cookie"}
    if logout:
        headers[settings.SHARED_CONSTANTS['header_keys']
                ['auth_logout']] = 'true'
    return HTTPException(
        status_code=status_code_and_detail['status_code'],
        detail=status_code_and_detail['detail'],
        headers=headers
    )


def multiple_authorization_types_provided(types: set[str]) -> StatusCodeAndDetail:
    return StatusCodeAndDetail(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Multiple authorization types provided: {}. Only one type may be provided".format(
            ", ".join(types))
    )


def missing_authorization() -> StatusCodeAndDetail:
    return StatusCodeAndDetail(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header or {} cookie".format(
            auth.ACCESS_TOKEN_COOKIE_KEY)
    )


def improper_format() -> StatusCodeAndDetail:
    return StatusCodeAndDetail(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Improper format for authorization token"
    )


def missing_required_claims() -> StatusCodeAndDetail:
    return StatusCodeAndDetail(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Missing required claims in authorization token"
    )


def authorization_expired() -> StatusCodeAndDetail:
    return StatusCodeAndDetail(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization expired"
    )


def user_not_found() -> StatusCodeAndDetail:
    return StatusCodeAndDetail(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
    )


def not_permitted() -> StatusCodeAndDetail:
    return StatusCodeAndDetail(
        status_code=status.HTTP_403_FORBIDDEN, detail="Not permitted"
    )


def credentials() -> StatusCodeAndDetail:
    return StatusCodeAndDetail(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials"
    )


def invalid_otp() -> StatusCodeAndDetail:
    return StatusCodeAndDetail(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid OTP"
    )


def authorization_type_not_permitted() -> StatusCodeAndDetail:
    return StatusCodeAndDetail(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Authorization type not permitted for this endpoint"
    )
