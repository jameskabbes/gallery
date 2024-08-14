from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query, status, Response, Depends
from fastapi.security import OAuth2AuthorizationCodeBearer, OAuth2PasswordRequestForm
from gallery import get_client, custom_types, models, utils
import datetime
from sqlmodel import Session, SQLModel, select
import typing
import httpx
import jwt

from google.oauth2 import id_token
from google.auth.transport import requests


class DetailOnlyResponse(typing.TypedDict):
    detail: str


class NotFoundResponse(DetailOnlyResponse):
    pass


class SuccessfulDeleteResponse(DetailOnlyResponse):
    ok: bool


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('startingup')
    yield
    print('closingdown')


app = FastAPI(lifespan=lifespan)
c = get_client()
c.create_tables()


@app.get('/')
async def read_root():
    return {"home": datetime.datetime.now()}


@app.get('/studios/{studio_id}/',  responses={status.HTTP_404_NOT_FOUND: {"description": 'Studio not found', 'model': NotFoundResponse}})
async def get_studio(studio_id: custom_types.StudioID) -> models.StudioPublic:
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
async def patch_studio(studio_id: custom_types.StudioID, studio: models.StudioUpdate) -> models.StudioPublic:

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
async def delete_studio(studio_id: custom_types.StudioID):
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
async def get_pages_studio(studio_id: custom_types.StudioID) -> PagesStudioResponse:
    d: PagesStudioResponse = {
        'studio': await get_studio(studio_id)
    }
    return d


# user

class LoginRequest(typing.TypedDict):
    email: str
    password: str


class Token(typing.TypedDict):
    access_token: str
    token_type: str


@app.post('/token/', responses={status.HTTP_401_UNAUTHORIZED: {"description": 'Invalid email or password'}})
async def token(login_data: LoginRequest) -> Token:
    email = login_data['email']
    password = login_data['password']

    with Session(c.db_engine) as session:
        user = session.exec(select(models.User).where(
            models.User.email == email)).first()

        if not user or not utils.verify_password(password, user.hashed_password):
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, detail='Invalid email or password')

        payload = {
            "sub": user.email,
            "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=1)
        }

        access_token = jwt.encode(payload, '1234', algorithm='HS256')
        token: Token = {"access_token": access_token, "token_type": "bearer"}
        return token


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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
