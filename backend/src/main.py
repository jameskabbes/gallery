from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query, status, Response, Depends
from fastapi.security import OAuth2AuthorizationCodeBearer, OAuth2PasswordRequestForm, OAuth2PasswordBearer
from gallery import get_client, models, utils, config
import datetime
from sqlmodel import Session, SQLModel, select
import typing
import httpx
import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel
import datetime

from google.oauth2 import id_token
from google.auth.transport import requests

SECRET_KEY = config.DATA_DIR.joinpath('jwt_secret_key.txt').read_text()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


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


class DetailOnlyResponse(typing.TypedDict):
    detail: str


class NotFoundResponse(DetailOnlyResponse):
    pass


class SuccessfulDeleteResponse(DetailOnlyResponse):
    ok: bool


@app.get('/')
async def read_root():
    return {"home": datetime.datetime.now()}


# user

def create_access_token(data: dict, expires_delta: datetime.timedelta = datetime.timedelta(minutes=15)) -> str:
    to_encode = data.copy()
    to_encode.update(
        {"exp": datetime.datetime.now(datetime.UTC) + expires_delta})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: typing.Annotated[str, Depends(oauth2_scheme)]) -> models.User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except InvalidTokenError:
        raise CREDENTIALS_EXCEPTION

    user_id = models.User.import_from_token_payload(payload)
    if not user_id:
        raise CREDENTIALS_EXCEPTION

    with Session(c.db_engine) as session:
        user = session.get(models.User, user_id)
        if not user:
            raise CREDENTIALS_EXCEPTION
        return user


@app.post("/token/")
async def login_for_access_token(
    form_data: typing.Annotated[OAuth2PasswordRequestForm, Depends()],
) -> models.Token:
    with Session(c.db_engine) as session:
        user = models.User.authenticate(
            session, form_data.username, form_data.password)

        print(user)

        if not user:
            raise CREDENTIALS_EXCEPTION
        access_token = create_access_token(
            data=user.export_for_token_payload(), expires_delta=datetime.timedelta(
                minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return models.Token(access_token=access_token, token_type="bearer")


@app.get("/users/me")
async def read_users_me(
    current_user: typing.Annotated[models.User, Depends(get_current_user)],
):
    return current_user


@app.get('/users/{user_id}/',  responses={status.HTTP_404_NOT_FOUND: {"description": 'User not found', 'model': NotFoundResponse}})
async def get_user_by_id(user_id: models.UserTypes.id) -> models.UserPublic:
    with Session(c.db_engine) as session:
        user = session.get(models.User, user_id)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail='User not found')
        return user


@app.get('/users/username/{user_id}/',  responses={status.HTTP_404_NOT_FOUND: {"description": 'User not found', 'model': NotFoundResponse}})
async def get_user_by_username(username: models.UserTypes.username) -> models.UserPublic:
    with Session(c.db_engine) as session:
        user = session.exec(select(models.User).where(
            models.User.username == username)).first()
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail='User not found')
        return user


@app.post('/users/', responses={status.HTTP_409_CONFLICT: {"description": 'User already exists', 'model': DetailOnlyResponse}})
async def post_user(user: models.UserCreate) -> models.UserPublic:

    with Session(c.db_engine) as session:

        existing_username = session.exec(select(models.User).where(
            models.User.username == user.username)).first()
        existing_email = session.exec(select(models.User).where(
            models.User.email == user.email)).first()

        if existing_username or existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail='User already exists')

        db_user = models.User(
            id=models.User.generate_id(),  **user.model_dump(), hashed_password=utils.hash_password(user.password))
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

        return db_user


class ItemAvailableResponse(typing.TypedDict):
    available: bool


@app.get('/users/available/username/{username}/')
async def user_username_available(username: models.UserTypes.username) -> ItemAvailableResponse:

    if len(username) < 1:
        return {'available': False}

    with Session(c.db_engine) as session:
        user = session.exec(select(models.User).where(
            models.User.username == username)).first()
        if user:
            return {'available': False}
        else:
            return {'available': True}


@app.get('/users/available/email/{email}/')
async def user_username_exists(email: models.UserTypes.email) -> ItemAvailableResponse:

    with Session(c.db_engine) as session:
        user = session.exec(select(models.User).where(
            models.User.email == email)).first()
        if user:
            return {"available": False}
        else:
            return {"available": True}

# Studio


@app.get('/studios/{studio_id}/',  responses={status.HTTP_404_NOT_FOUND: {"description": 'Studio not found', 'model': NotFoundResponse}})
async def get_studio(studio_id: models.StudioTypes.id) -> models.StudioPublic:
    with Session(c.db_engine) as session:
        studio = session.get(models.Studio, studio_id)
        if not studio:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail='Studio not found')
        return studio


@app.post('/studios/')
async def post_studio(studio: models.StudioCreate) -> models.StudioPublic:

    with Session(c.db_engine) as session:
        db_studio = models.Studio(
            id=models.Studio.generate_id(), **studio.model_dump())

        session.add(db_studio)
        session.commit()
        session.refresh(db_studio)
        return db_studio


@app.patch('/studios/{studio_id}/', responses={status.HTTP_404_NOT_FOUND: {"description": 'Studio not found', 'model': NotFoundResponse}})
async def patch_studio(studio_id: models.StudioTypes.id, studio: models.StudioUpdate) -> models.StudioPublic:

    with Session(c.db_engine) as session:
        db_studio = session.get(models.Studio, studio_id)
        if not db_studio:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail='Studio not found')
        db_studio.sqlmodel_update(studio.model_dump(exclude_unset=True))
        session.add(db_studio)
        session.commit()
        session.refresh(db_studio)
        return db_studio


@app.delete('/studios/{studio_id}/', status_code=204, responses={404: {"description": 'Studio not found', 'model': NotFoundResponse}})
async def delete_studio(studio_id: models.StudioTypes.id):
    with Session(c.db_engine) as session:
        studio = session.get(models.Studio, studio_id)
        if not studio:
            raise HTTPException(status_code=404, detail='Studio not found')
        session.delete(studio)
        session.commit()
        return Response(status_code=204)


@app.get('/studios/')
async def get_studios(offset: int = Query(default=0, ge=0), limit: int = Query(default=100, ge=0, le=100)) -> list[models.StudioPublic]:
    print(offset, limit)

    with Session(c.db_engine) as session:
        studios = session.exec(
            select(models.Studio).offset(offset).limit(limit)).all()
        return studios

#


@ app.post("/auth/google/")
async def google_auth(token_request):
    token = token_request.token

    print('token', token)

    # Verify the token with Google
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={token}")
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid Google token")

        user_info = response.json()
        print(user_info)

        return user_info
        # email = user_info.get("email")
        # name = user_info.get("name")
        # picture = user_info.get("picture")

        # # Create a JWT token for the user
        # user_token = jwt.encode(
        #     {"email": email, "name": name, "picture": picture}, SECRET_KEY, algorithm="HS256")

        # return {"token": user_token}


# Pages


class PagesStudiosResponse(typing.TypedDict):
    studios: list[models.StudioPublic]


@app.get('/pages/studios/')
async def get_pages_studios() -> PagesStudiosResponse:
    d: PagesStudiosResponse = {
        'studios': await get_studios(offset=0, limit=100)
    }
    return d


class PagesStudioResponse(typing.TypedDict):
    studio: models.StudioPublic


@app.get('/pages/studios/{studio_id}/', responses={404: {"description": 'Studio not found', 'model': NotFoundResponse}})
async def get_pages_studio(studio_id: models.StudioTypes.id) -> PagesStudioResponse:
    d: PagesStudioResponse = {
        'studio': await get_studio(studio_id)
    }
    return d


@app.get('/pages/profile/', responses={status.HTTP_401_UNAUTHORIZED: {"description": 'Unauthorized', 'model': DetailOnlyResponse}})
async def get_pages_profile(current_user: models.User = Depends(get_current_user)) -> models.User:
    return current_user

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
