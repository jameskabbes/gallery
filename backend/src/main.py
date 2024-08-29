from fastapi import FastAPI, HTTPException, Query, status, Response, Depends, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from contextlib import asynccontextmanager
from gallery import get_client, models, utils, config, auth
import datetime
from sqlmodel import Session, SQLModel, select
import typing
import httpx
import jwt
from jwt.exceptions import InvalidTokenError, MissingRequiredClaimError, DecodeError
from pydantic import BaseModel
import datetime
from functools import wraps
import logging

from google.oauth2 import id_token
from google.auth.transport import requests


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('startingup')
    yield
    print('closingdown')


logging.basicConfig(level=logging.DEBUG)

app = FastAPI(lifespan=lifespan)
c = get_client()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token/", auto_error=False)


class DetailOnlyResponse(BaseModel):
    detail: str


class NotFoundResponse(DetailOnlyResponse):
    pass


def create_access_token(data: typing.Annotated[dict, 'The data to encode'], expiry_datetime: typing.Annotated[typing.Optional[datetime.timedelta], 'The datetime the token expires'] = None) -> str:

    dt_now: datetime.datetime = datetime.datetime.now(datetime.UTC)

    to_encode = data.copy()
    to_encode.update({"iat": dt_now.timestamp()})
    if expiry_datetime != None:
        to_encode.update({"exp": (dt_now + expiry_datetime).timestamp()})

    return jwt.encode(to_encode, c.jwt_secret_key, algorithm=c.jwt_algorithm)


class GetTokenReturn(BaseModel):
    payload: dict | None = None
    exception: auth.EXCEPTION | None = None


def get_token(token: typing.Annotated[str, Depends(oauth2_scheme)]) -> GetTokenReturn:

    try:
        payload = jwt.decode(token, c.jwt_secret_key,
                             algorithms=[c.jwt_algorithm])
    except:
        return GetTokenReturn(exception='invalid_token')

    for claim in auth.TOKEN_REQUIRED_CLAIMS:
        if claim not in payload:
            return GetTokenReturn(exception='missing_required_claims')

    return GetTokenReturn(payload=payload)


class GetAuthReturn(BaseModel):
    user: models.UserPublic | None = None
    exception: auth.EXCEPTION | None = None


async def get_auth(token_return: GetTokenReturn, expiry_timedelta: typing.Annotated[datetime.timedelta, 'The timedelta from token creation in which the token is still valid'] = c.authentication['default_expiry_timedelta']) -> GetAuthReturn:

    if 'exception' in token_return or not token_return.payload:
        return GetAuthReturn(exception='invalid_token')

    token_payload = token_return.payload
    dt_now = datetime.datetime.now(datetime.UTC)

    if 'exp' in token_payload:
        dt_exp = datetime.datetime.fromtimestamp(
            token_payload.get('exp'), datetime.UTC)

        if dt_now > dt_exp:
            return GetAuthReturn(exception='token_expired')

    else:
        dt_iat = datetime.datetime.fromtimestamp(
            token_payload.get('iat'), datetime.UTC)

        if dt_now > (dt_iat + expiry_timedelta):
            return GetAuthReturn(exception='token_expired')

    # check if token has user id
    user_id = models.User.import_from_token_payload(token_payload)
    if not user_id:
        return GetAuthReturn(exception='missing_required_claims')

    # check if user exists
    with Session(c.db_engine) as session:
        user = session.get(models.User, user_id)
        if not user:
            return GetAuthReturn(exception='user_not_found')
        return GetAuthReturn(user=models.UserPublic.model_validate(user))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors()},
    )


# USERS

@app.get('/users/{user_id}', responses={status.HTTP_404_NOT_FOUND: {"description": models.User.not_found_message(), 'model': NotFoundResponse}})
async def get_user_by_id(user_id: models.UserTypes.id) -> models.UserPublic:

    with Session(c.db_engine) as session:
        user = models.User.get_by_id(session, user_id)

        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail=models.User.not_found_message())
        else:
            return user


@app.get('/users/username/{username}', responses={status.HTTP_404_NOT_FOUND: {"description": models.User.not_found_message(), 'model': NotFoundResponse}})
async def get_user_by_username(username: models.UserTypes.username) -> models.UserPublic:

    with Session(c.db_engine) as session:
        user = models.User.get_by_key_value(session, 'username', username)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail=models.User.not_found_message())
        else:
            return user


@ app.post('/users/', responses={status.HTTP_409_CONFLICT: {"description": 'User already exists', 'model': DetailOnlyResponse}})
async def post_user(user_create: models.UserCreate) -> models.UserPrivate:

    with Session(c.db_engine) as session:
        existing_username = models.User.get_by_key_value(
            session, 'username', user_create.username)
        existing_email = models.User.get_by_key_value(
            session, 'email', user_create.email)

        if existing_username or existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail='User already exists')

        user = user_create.create()
        user.add_to_db(session)
        return user


@app.patch('/users/{user_id}/', responses={
    status.HTTP_401_UNAUTHORIZED: {'description': 'Invalid token', 'model': DetailOnlyResponse},
    status.HTTP_403_FORBIDDEN: {"description": 'User does not have permission to update this user', 'model': DetailOnlyResponse},
    status.HTTP_404_NOT_FOUND: {"description": models.User.not_found_message(), 'model': NotFoundResponse},
    status.HTTP_409_CONFLICT: {"description": 'Username or email already exists', 'model': DetailOnlyResponse},
})
async def patch_user(user_id: models.UserTypes.id, user_update: models.UserUpdate, token_return: typing.Annotated[GetTokenReturn, Depends(get_token)]) -> models.UserPublic:

    auth_return = await get_auth(token_return)
    if auth_return.exception:
        raise auth.EXCEPTION_MAPPING[auth_return.exception]

    with Session(c.db_engine) as session:

        user = models.User.get_by_id(session, user_id)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail=models.User.not_found_message())

        if user.id != auth_return.user.id:
            raise HTTPException(status.HTTP_403_FORBIDDEN,
                                detail='User does not have permission to update this user')

        # if they changed their username, check if it's available
        if user_update.username != None:
            if user.username != user_update.username:
                if models.User.key_value_exists(session, 'username', user_update.username):
                    raise HTTPException(status.HTTP_409_CONFLICT,
                                        detail='Username already exists')

        # if they changed their email, check if it's available
        if user_update.email != None:
            if user.email != user_update.email:
                if models.User.key_value_exists(session, 'email', user_update.email):
                    raise HTTPException(status.HTTP_409_CONFLICT,
                                        detail='Email already exists')

        update_fields = {}
        if user_update.email != None:
            update_fields['email'] = user_update.email
        if user_update.username != None:
            update_fields['username'] = user_update.username
        if user_update.password != None:
            update_fields['hashed_password'] = utils.hash_password(
                user_update.password)

        user.sqlmodel_update(update_fields)
        session.add(user)
        session.commit()
        return models.UserPublic.model_validate(user)


@ app.delete('/users/{user_id}/', status_code=204, responses={status.HTTP_404_NOT_FOUND: {"description": models.User.not_found_message(), 'model': NotFoundResponse}})
async def delete_user(user_id: models.UserTypes.id):

    with Session(c.db_engine) as session:
        user = models.User.get_by_id(session, user_id)

        if not user:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, detail=models.User.not_found_message())

        session.delete(user)
        session.commit()
        return Response(status_code=204)


class ItemAvailableResponse(BaseModel):
    available: bool


@ app.get('/users/available/username/{username}/')
async def user_username_available(username: models.UserTypes.username) -> ItemAvailableResponse:

    with Session(c.db_engine) as session:
        if len(username) < 1:
            return ItemAvailableResponse(available=False)

        with Session(c.db_engine) as session:
            if models.User.key_value_exists(session, 'username', username):
                return ItemAvailableResponse(available=False)
            else:
                return ItemAvailableResponse(available=True)


@ app.get('/users/available/email/{email}/')
async def user_username_exists(email: models.UserTypes.email) -> ItemAvailableResponse:

    with Session(c.db_engine) as session:
        user = session.exec(select(models.User).where(
            models.User.email == email)).first()
        if user:
            return {"available": False}
        else:
            return {"available": True}


assert c.root_config['auth_key'] == 'auth'


@ app.post("/token/")
async def post_token(
    form_data: typing.Annotated[OAuth2PasswordRequestForm, Depends()],
) -> models.Token:
    with Session(c.db_engine) as session:
        user = models.User.authenticate(
            session, form_data.username, form_data.password)
        if not user:
            raise auth.CREDENTIALS_EXCEPTION

        access_token = create_access_token(
            data=user.export_for_token_payload())

        return models.Token(access_token=access_token)


class AuthResponse(BaseModel):
    auth: GetAuthReturn


class LoginResponse(AuthResponse):
    token: models.Token


@ app.post('/login/', responses={status.HTTP_401_UNAUTHORIZED: {'description': 'Could not validate credentials', 'model': DetailOnlyResponse}})
async def login(form_data: typing.Annotated[OAuth2PasswordRequestForm, Depends()]) -> LoginResponse:

    with Session(c.db_engine) as session:
        user = models.User.authenticate(
            session, form_data.username, form_data.password)
        if not user:
            raise auth.CREDENTIALS_EXCEPTION

        access_token = create_access_token(
            data=user.export_for_token_payload())

        return LoginResponse(
            auth=GetAuthReturn(user=models.UserPublic.model_validate(user)),
            token=models.Token(access_token=access_token)
        )


class SignupResponse(AuthResponse):
    user: models.UserPrivate
    token: models.Token


@ app.post('/signup/', responses={status.HTTP_409_CONFLICT: {"description": 'User already exists', 'model': DetailOnlyResponse}})
async def signup(user_create: models.UserCreate) -> SignupResponse:
    user = await post_user(user_create)
    access_token = create_access_token(data=user.export_for_token_payload())

    return SignupResponse(
        auth=GetAuthReturn(user=models.UserPublic.model_validate(user)),
        user=user,
        token=models.Token(access_token=access_token)
    )


class PagesProfileResponse(AuthResponse):
    user: models.UserPrivate | None = None


@ app.get('/pages/profile/')
async def get_pages_profile(token_return: typing.Annotated[GetTokenReturn, Depends(get_token)]) -> PagesProfileResponse:

    auth_return = await get_auth(token_return)
    if auth_return.exception:
        raise auth.EXCEPTION_MAPPING[auth_return.exception]

    with Session(c.db_engine) as session:
        user = models.User.get_by_id(session, auth_return.user.id)
        if user is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail=models.User.not_found_message())

        # convert user to models.UserPrivate
        return PagesProfileResponse(
            auth=auth_return,
            user=models.UserPrivate.model_validate(user)
        )


class PagesHomeResponse(AuthResponse):
    pass


@ app.get('/pages/home/')
async def get_pages_home(token_return: typing.Annotated[GetTokenReturn, Depends(get_token)]) -> PagesHomeResponse:

    auth_return = await get_auth(token_return)
    return PagesHomeResponse(
        auth=auth_return
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
