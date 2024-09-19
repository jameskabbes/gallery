from fastapi import HTTPException, status
import typing
import jwt
import datetime
from gallery import models
from pydantic import BaseModel


class SCOPES:
    USERS_READ = 'users.read'
    USERS_WRITE = 'users.write'


type Token = str
type APIKey = str
type BearerString = Token | APIKey
type BearerType = typing.Literal['token', 'api_key']

INVALID_BEARER_EXCEPTION = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Invalid bearer",
    headers={"WWW-Authenticate": "Bearer"})

MISSING_REQUIRED_CLAIMS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Missing required claims",
    headers={"WWW-Authenticate": "Bearer"})

# Token
INVALID_TOKEN_EXCEPTION = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Invalid token",
    headers={"WWW-Authenticate": "Bearer"})


TOKEN_EXPIRED_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Token expired",
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
    detail="Incorrect username or password",
    headers={"WWW-Authenticate": "Bearer"})

type EXCEPTION = typing.Literal['invalid_bearer', 'invalid_token', 'token_expired',
                                'missing_required_claims', 'user_not_found', 'user_not_permitted', 'credentials']

EXCEPTION_MAPPING: dict[EXCEPTION, HTTPException] = {
    'invalid_bearer': INVALID_BEARER_EXCEPTION,
    'invalid_token': INVALID_TOKEN_EXCEPTION,
    'token_expired': TOKEN_EXPIRED_EXCEPTION,
    'missing_required_claims': MISSING_REQUIRED_CLAIMS_EXCEPTION,
    'user_not_found': USER_NOT_FOUND_EXCEPTION,
    'user_not_permitted': USER_NOT_PERMITTED_EXCEPTION,
    'credentials': CREDENTIALS_EXCEPTION
}


class VerifyTokenReturn(BaseModel):
    user: models.UserPrivate = None
    exception: EXCEPTION | None = None


# def _verify_token(token_payload: dict, expiry_timedelta: datetime.timedelta):

#     if 'iat' not in token_payload:
#         return VerifyTokenReturn(exception='missing_required_claims')

#     dt_iat = datetime.datetime.fromtimestamp(
#         token_payload.get('iat'), datetime.UTC)

#     dt_now = datetime.datetime.now(datetime.UTC)
#     if dt_now > (dt_iat + expiry_timedelta):
#         return VerifyTokenReturn(exception='token_expired')

#     # check if token has user id
#     user_id = models.User.import_from_token_payload(token_payload)
#     if not user_id:
#         return VerifyTokenReturn(exception='missing_required_claims')

#     # check if user exists
#     with Session(c.db_engine) as session:
#         user = session.get(models.User, user_id)
#         if not user:
#             return VerifyTokenReturn(exception='user_not_found')
#         return VerifyTokenReturn(user=models.UserPrivate.model_validate(user))


TOKEN_REQUIRED_CLAIMS: list[str] = ['iat', models.User._payload_claim]

# api_key

INVALID_API_KEY_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid API key",
    headers={"WWW-Authenticate": "Bearer"})


INSUFFICIENT_SCOPE_EXCEPTION = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Insufficient scope for API key",
    headers={"WWW-Authenticate": "Bearer"})
