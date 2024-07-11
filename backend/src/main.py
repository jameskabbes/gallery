from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from gallery import get_client, custom_types, models
import datetime
from sqlmodel import Session, SQLModel, select
import typing


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('startingup')
    yield
    print('closingdown')

app = FastAPI(lifespan=lifespan)
c = get_client()


@app.get('/')
async def read_root():
    return {"home": datetime.datetime.now()}


@app.get('/studios/{studio_id}')
async def get_studio(studio_id: custom_types.StudioID) -> models.StudioPublic:
    with Session(c.db_engine) as session:
        studio = session.get(models.Studio, studio_id)
        if not studio:
            raise HTTPException(status_code=404, detail='Studio not found')
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


@app.patch('/studios/{studio_id}')
async def patch_studio(studio_id: custom_types.StudioID, studio: models.StudioUpdate) -> models.StudioPublic:

    with Session(c.db_engine) as session:
        db_studio = session.get(models.Studio, studio_id)
        if not db_studio:
            raise HTTPException(status_code=404, detail='Studio not found')
        db_studio.sqlmodel_update(studio.model_dump(exclude_unset=True))
        session.add(db_studio)
        session.commit()
        session.refresh(db_studio)
        return db_studio


@app.delete('/studios/{studio_id}')
async def delete_studio(studio_id: custom_types.StudioID):
    with Session(c.db_engine) as session:
        studio = session.get(models.Studio, studio_id)
        if not studio:
            raise HTTPException(status_code=404, detail='Studio not found')
        session.delete(studio)
        session.commit()
        return {'ok': True}


@ app.get('/studios/')
async def get_studios(offset: int = 0, limit: int = Query(default=100, le=100)) -> list[models.StudioPublic]:
    with Session(c.db_engine) as session:
        objects = session.exec(
            select(models.Studio).offset(offset).limit(limit)).all()
        return objects
