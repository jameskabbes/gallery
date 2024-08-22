from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query, status, Response, Depends
from fastapi.security import OAuth2AuthorizationCodeBearer, OAuth2PasswordRequestForm, OAuth2PasswordBearer
from gallery import get_client, models, utils, config
import datetime
from sqlmodel import Session, SQLModel, select
import typing
import httpx
import jwt
from jwt.exceptions import InvalidTokenError, MissingRequiredClaimError, DecodeError
from pydantic import BaseModel
import datetime
from functools import wraps

from google.oauth2 import id_token
from google.auth.transport import requests


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('startingup')
    yield
    print('closingdown')


app = FastAPI(lifespan=lifespan)
c = get_client()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


class DetailOnlyResponse(BaseModel):
    detail: str


class NotFoundResponse(DetailOnlyResponse):
    pass


@app.get('/')
async def read_root():
    return {"home": datetime.datetime.now()}


# user


def create_access_token(data: typing.Annotated[dict, 'The data to encode'], expiry_datetime: typing.Annotated[typing.Optional[datetime.timedelta], 'The datetime the token expires'] = None) -> str:

    dt_now: datetime.datetime = datetime.datetime.now(datetime.UTC)

    to_encode = data.copy()
    to_encode.update({"iat": dt_now.timestamp()})
    if expiry_datetime != None:
        to_encode.update({"exp": (dt_now + expiry_datetime).timestamp()})

    return jwt.encode(to_encode, c.jwt_secret_key, algorithm=c.jwt_algorithm)


type GetSessionReturn = typing.Generator[Session, None, None]


def get_session() -> GetSessionReturn:
    with Session(c.db_engine) as session:
        yield session


class TokenExpiredError(InvalidTokenError):
    def __str__(self) -> str:
        return 'Token has expired'


class GetAuthVerboseReturn(BaseModel):
    user: models.UserPublic | None = None
    exception: Exception | None = None

    class Config:
        arbitrary_types_allowed: typing.ClassVar[bool] = True


async def get_auth_verbose(token: typing.Annotated[str, Depends(oauth2_scheme)], expiry_timedelta: typing.Annotated[datetime.timedelta, 'The timedelta from token creation in which the token is still valid'] = c.authentication['default_expiry_timedelta']
                           ) -> GetAuthVerboseReturn:

    # check if token is proper format
    try:
        payload = jwt.decode(token, c.jwt_secret_key,
                             algorithms=[c.jwt_algorithm])
    except:
        return GetAuthVerboseReturn(exception=DecodeError('Invalid token'))

    # iat must be present
    if 'iat' not in payload:
        return GetAuthVerboseReturn(exception=MissingRequiredClaimError('iat not present'))

    dt_now = datetime.datetime.now(datetime.UTC)

    if 'exp' in payload:
        dt_exp = datetime.datetime.fromtimestamp(
            payload.get('exp'), datetime.UTC)

        if dt_now > dt_exp:
            return GetAuthVerboseReturn(exception=TokenExpiredError)

    else:
        dt_iat = datetime.datetime.fromtimestamp(
            payload.get('iat'), datetime.UTC)

        if dt_now > (dt_iat + expiry_timedelta):
            return GetAuthVerboseReturn(exception=TokenExpiredError)

    # check if token has user id
    user_id = models.User.import_from_token_payload(payload)
    if not user_id:
        return GetAuthVerboseReturn(exception=MissingRequiredClaimError(models.User._payload_claim + ' not present'))

    # check if user exists
    with Session(c.db_engine) as session:
        user = session.get(models.User, user_id)
        if not user:
            return GetAuthVerboseReturn(exception=HTTPException(status.HTTP_404_NOT_FOUND, detail='User not found'))
        return GetAuthVerboseReturn(user=user)


class GetAuthReturn(BaseModel):
    user: typing.Optional[models.UserPublic]


async def get_auth(token: typing.Annotated[str, Depends(oauth2_scheme)], expiry_timedelta: typing.Annotated[datetime.timedelta, 'The timedelta from token creation in which the token is still valid'] = c.authentication['default_expiry_timedelta']
                   ) -> GetAuthReturn:
    auth_verbose = await get_auth_verbose(token, expiry_timedelta)
    return GetAuthReturn(user=auth_verbose.user)


class GetSessionAndAuthReturn(BaseModel):
    session: GetSessionReturn
    auth: GetAuthReturn

    class Config:
        arbitrary_types_allowed: typing.ClassVar[bool] = True


def get_session_and_auth(session: Session = Depends(get_session), user: GetAuthReturn = Depends(get_auth)) -> GetSessionAndAuthReturn:
    return GetSessionAndAuthReturn(session=session, user=user)


class TokenReturn(BaseModel):
    token: models.Token
    user: models.UserPublic


@ app.post("/token/")
async def login_for_access_token(
    form_data: typing.Annotated[OAuth2PasswordRequestForm, Depends()],
) -> TokenReturn:
    with Session(c.db_engine) as session:
        user = models.User.authenticate(
            session, form_data.username, form_data.password)
        if not user:
            raise CREDENTIALS_EXCEPTION
        access_token = create_access_token(
            data=user.export_for_token_payload())

        token = models.Token(access_token=access_token, token_type="bearer")
        return {
            'user': user,
            'token': token
        }


# template

@app.get('/users/{user_id}', responses={status.HTTP_404_NOT_FOUND: {"description": models.User.not_found_message(), 'model': NotFoundResponse}})
async def get_user_by_id(user_id: models.UserTypes.id, session: Session = Depends(get_session)) -> models.UserPublic:
    user = models.User.get_by_id(session, user_id)

    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail=models.User.not_found_message())
    else:
        return user


@app.get('/users/username/{username}', responses={status.HTTP_404_NOT_FOUND: {"description": models.User.not_found_message(), 'model': NotFoundResponse}})
async def get_user_by_username(username: models.UserTypes.username, session: Session = Depends(get_session)) -> models.UserPublic:
    user = models.User.get_by_key_value(session, 'username', username)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail=models.User.not_found_message())
    else:
        return user


@ app.post('/users/', responses={status.HTTP_409_CONFLICT: {"description": 'User already exists', 'model': DetailOnlyResponse}})
async def post_user(user_create: models.UserCreate, session: Session = Depends(get_session)) -> models.UserPrivate:

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


@app.patch('/users/{user_id}', responses={status.HTTP_404_NOT_FOUND: {"description": models.User.not_found_message(), 'model': NotFoundResponse}})
async def patch_user(user_id: models.UserTypes.id, user_update: models.UserUpdate, session: Session = Depends(get_session)) -> models.UserPublic:

    user = models.User.get_by_id(session, user_id)

    # if they changed their username, check if it's available
    if user.username != user_update.username:
        if models.User.key_value_exists(session, 'username', user_update.username):
            raise HTTPException(status.HTTP_409_CONFLICT,
                                detail='Username already exists')

    # if they changed their email, check if it's available
    if user.email != user_update.email:
        if models.User.key_value_exists(session, 'email', user_update.email):
            raise HTTPException(status.HTTP_409_CONFLICT,
                                detail='Email already exists')

    user.sqlmodel_update(
        email=user_update.email, username=user_update.username, hashed_password=utils.hash_password(user_update.password))

    session.add(user)
    session.commit()
    return user


@app.delete('/users/{user_id}', status_code=204, responses={status.HTTP_404_NOT_FOUND: {"description": models.User.not_found_message(), 'model': NotFoundResponse}})
async def delete_user(user_id: models.UserTypes.id, session: Session = Depends(get_session)):

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
async def user_username_available(username: models.UserTypes.username, session: Session = Depends(get_session)) -> ItemAvailableResponse:

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

# Pages


class PagesBaseResponse(BaseModel):
    auth: GetAuthReturn


class PagesProfileResponse(PagesBaseResponse):
    user: models.UserPrivate


@ app.get('/pages/profile/', responses={status.HTTP_401_UNAUTHORIZED: {"description": 'Unauthorized', 'model': DetailOnlyResponse}, status.HTTP_404_NOT_FOUND: {"description": models.User.not_found_message(), 'model': NotFoundResponse}})
async def get_pages_profile(session_and_auth: GetSessionAndAuthReturn = Depends(get_session_and_auth)) -> PagesProfileResponse:

    session = session_and_auth.session
    auth = session_and_auth.auth

    if 'exception' in auth:
        raise CREDENTIALS_EXCEPTION

    user = models.User.get_by_id(session, auth.user.id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail=models.User.not_found_message())

    return PagesProfileResponse(auth=auth, user=user)


class PagesHomeResponse(PagesBaseResponse):
    pass


@ app.get('/pages/home/')
async def get_pages_home(session_and_auth: GetSessionAndAuthReturn = Depends(get_session_and_auth)) -> PagesHomeResponse:
    return PagesHomeResponse(auth=session_and_auth.auth)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
