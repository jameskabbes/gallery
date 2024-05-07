import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pymongo import MongoClient
from gallery import config, types, utils
from gallery.objects import studios, studio, events, event

import pydantic
import datetime
import typing
import os

app = FastAPI()

# Initialize PyMongo client
mongo_client = utils.get_pymongo_client()
db = mongo_client['gallery']


@app.get("/")
async def read_root():
    return {"home": datetime.datetime.now()}


class StudiosResponse(typing.TypedDict):
    studios: studios.Studios.PluralByIdType
    dir_names_to_add: set[studio.Types.dir_name]
    ids_to_delete: set[types.StudioId]


@app.get("/studios/")
async def get_studios() -> StudiosResponse:

    dir_names_to_add, studios_ids_to_delete = studios.Studios.get_add_and_delete(
        db[studios.Studios.COLLECTION_NAME])

    d: StudiosResponse = {}
    d['studios'] = studios.Studios.find(db[studios.Studios.COLLECTION_NAME])
    d['dir_names_to_add'] = dir_names_to_add
    d['ids_to_delete'] = studios_ids_to_delete

    return d


@app.post("/studios/{dir_name}/import/")
async def import_studio(dir_name: studio.Types.dir_name) -> StudiosResponse:

    # make sure this studio doesn't already exist
    if db[studios.Studios.COLLECTION_NAME].find_one({"dir_name": dir_name}):
        raise HTTPException(status_code=400, detail="Studio already exists")

    # make sure the dir already exists
    if not studios.Studios.DIR.joinpath(dir_name).exists():
        raise HTTPException(
            status_code=404, detail="Studio directory not found")

    new_studio = studio.Studio(
        _id=studio.Studio.generate_id(), dir_name=dir_name)
    new_studio.insert(db[studios.Studios.COLLECTION_NAME])

    return await get_studios()


@app.post("/studios/{studio_id}/delete/")
async def delete_studio(studio_id: types.StudioId) -> StudiosResponse:

    if not studio.Studio.exists(db[studios.Studios.COLLECTION_NAME], studio_id):
        raise HTTPException(status_code=404, detail="Studio not found")

    studio.Studio.delete_by_id(db[studios.Studios.COLLECTION_NAME], studio_id)
    return await get_studios()


class StudioResponse(typing.TypedDict):
    studio: studio.Studio
    events: events.Events.PluralByIdType


@app.get("/studio/{studio_id}/")
async def get_studio(studio_id: types.StudioId) -> StudioResponse:

    print(studio_id)

    d: StudioResponse = {}
    d['studio'] = studio.Studio.find_by_id(
        db[studios.Studios.COLLECTION_NAME], studio_id)
    d['events'] = {}

    return d


@app.get("/events/")
async def get_events() -> events.Events.PluralByIdType:
    return events.Events.find(db[events.Events.COLLECTION_NAME])


if __name__ == "__main__":
    uvicorn.run("app:app", port=config.UVICORN_PORT, reload=True)
