import typing
from fastapi import Request, HTTPException, status, Response
from arbor_imago import types, auth, config


class StatusCodeAndDetail(typing.TypedDict):
    status_code: int
    detail: str


def Base(status_code_and_detail: StatusCodeAndDetail, logout: bool = True) -> HTTPException:
    headers = {"WWW-Authenticate": "Bearer, Cookie"}
    if logout:
        headers[config.HEADER_KEYS
                ['auth_logout']] = 'true'
    return HTTPException(
        status_code=status_code_and_detail['status_code'],
        detail=status_code_and_detail['detail'],
        headers=headers
    )


def different_tokens_provided(types: set[str], n: int) -> StatusCodeAndDetail:
    return StatusCodeAndDetail(
        status_code=status.HTTP_400_BAD_REQUEST, detail="{n} different tokens provided from the following sources: {}. Only one unique token may be provided".format(
            n, ", ".join(types))
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


def missing_required_claims(claims: set[str]) -> StatusCodeAndDetail:
    return StatusCodeAndDetail(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Missing required claims: {}".format(
            ", ".join(claims))
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


def authorization_type_not_permitted(type: types.AuthCredential.type) -> StatusCodeAndDetail:
    return StatusCodeAndDetail(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Authorization type '{}' not permitted for this endpoint".format(
            type)
    )
