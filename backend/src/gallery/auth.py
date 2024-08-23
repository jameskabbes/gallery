from fastapi import HTTPException, status
import typing
import jwt
import datetime
from gallery import models

INVALID_TOKEN_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid token",
    headers={"WWW-Authenticate": "Bearer"})

TOKEN_EXPIRED_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Token expired",
    headers={"WWW-Authenticate": "Bearer"})

MISSING_REQUIRED_CLAIMS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Missing required claims",
    headers={"WWW-Authenticate": "Bearer"})

USER_NOT_FOUND_EXCEPTION = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User not found")

USER_NOT_PERMITTED_EXCEPTION = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="User does not have permissions",
    headers={"WWW-Authenticate": "Bearer"})

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"})

type EXCEPTION = typing.Literal['invalid_token', 'token_expired',
                                'missing_required_claims', 'user_not_found', 'user_not_permitted', 'credentials']

EXCEPTION_MAPPING: dict[EXCEPTION, HTTPException] = {
    'invalid_token': INVALID_TOKEN_EXCEPTION,
    'token_expired': TOKEN_EXPIRED_EXCEPTION,
    'missing_required_claims': MISSING_REQUIRED_CLAIMS_EXCEPTION,
    'user_not_found': USER_NOT_FOUND_EXCEPTION,
    'user_not_permitted': USER_NOT_PERMITTED_EXCEPTION,
    'credentials': CREDENTIALS_EXCEPTION
}


TOKEN_REQUIRED_CLAIMS: list[str] = ['iat', models.User._payload_claim]
