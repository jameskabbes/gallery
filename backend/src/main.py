from fastapi import FastAPI
from gallery import get_client, custom_types, models
import datetime
from sqlmodel import Session, SQLModel

app = FastAPI()

# get the gallery client
c = get_client()


@app.get('/')
async def read_root():
    return {"home": datetime.datetime.now()}


@app.get('/studio/{studio_id}')
async def get_studio(studio_id: custom_types.StudioID) -> models.Studio:
    with Session(c.db_engine) as session:
        return models.Studio.get_from_db_by_id(session, studio_id)
