from fastapi import HTTPException, status
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pymongo import MongoClient
from gallery import config, types, utils
from gallery.objects import media, studio, event, client, media_types

import pydantic
import datetime
import typing
import os

app = FastAPI()

# get the gallery client
c = client.Client()


@app.get("/")
async def read_root():
    return {"home": datetime.datetime.now()}


class StudiosResponse(typing.TypedDict):
    studios: dict[types.StudioId, studio.Studio]
    studios_to_add: dict[types.StudioId, studio.Studio]
    studio_ids_to_delete: dict[types.StudioId, None]


@app.get("/studios/")
async def get_studios() -> StudiosResponse:
    studio_id_keys_to_add, studios_ids_to_delete = studio.Studio.find_to_add_and_delete(
        c.db[studio.Studio.COLLECTION_NAME], c.studios_dir)

    studios_to_add = {}
    for studio_id_keys in studio_id_keys_to_add:
        studio_inst = studio.Studio.make_from_id_keys(studio_id_keys)
        studios_to_add[studio_inst.id] = studio_inst

    d: StudiosResponse = {}
    d['studios'] = studio.Studio.get_all(c.db[studio.Studio.COLLECTION_NAME])
    d['studios_to_add'] = studios_to_add
    d['studio_ids_to_delete'] = {
        studio_id: None for studio_id in studios_ids_to_delete}

    return d


@app.post("/studios/")
async def create_studio(given_studio: studio.Studio):

    if studio.Studio.id_exists(c.db[studio.Studio.COLLECTION_NAME], given_studio.id):
        raise HTTPException(status_code=400, detail="Studio already exists")

    result = given_studio.insert(c.db[studio.Studio.COLLECTION_NAME])

    # make sure this was successful
    if result.inserted_id == None:
        raise HTTPException(
            status_code=500, detail="Failed to insert studio into database")


@app.delete("/studios/{studio_id}")
async def delete_studio(studio_id: types.StudioId):
    # Query the database to delete the studio
    result = studio.Studio.delete_by_id(
        c.db[studio.Studio.COLLECTION_NAME], studio_id)

    # Check if a studio was actually deleted
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Studio not found")

    # Return a message indicating the deletion was successful
    return {"message": "Studio deleted successfully"}
"""

@app.put("/studios/{studio_id}")
async def update_studio(studio_id: types.StudioId, given_studio: studio.Studio):
    # Get the studio from the database
    studio_inst = studio.Studio.get_by_id(
        c.db[studio.Studio.COLLECTION_NAME], studio_id)
    if studio_inst == None:
        raise HTTPException(status_code=404, detail="Studio not found")

    if studio_inst.dir_name is not None:

        # Update the studio
    if studio_update.dir_name is not None:
        studio_inst.dir_name = studio_update.dir_name
    if studio_update.name is not None:
        studio_inst.name = studio_update.name

    # Save the updated studio to the database
    studio_inst.save(c.db[studio.Studio.COLLECTION_NAME])

    return studio_inst
"""


@app.get('/file/{file_id}/content/')
async def get_file(file_id: types.MediaIdType) -> FileResponse:

    media_file_dict = media.Media.find_by_id(
        c.db[media.Media.COLLECTION_NAME], file_id, {'media_type': 1})

    if media_file_dict == None:
        raise HTTPException(status_code=404, detail="File not found")

    media_type: types.MediaType = media_file_dict['media_type']
    if media_type not in media_types.TYPES:
        raise HTTPException(status_code=404, detail="Media type not found")

    file_class = media_types.FILE_CLASS_MAPPING[media_type]
    file_obj = file_class.get_by_id(c.db[media.Media.COLLECTION_NAME], file_id)
    if file_obj == None:
        raise HTTPException(status_code=404, detail="File not found")

    event_obj = event.Event.get_by_id(
        c.db[event.Event.COLLECTION_NAME], file_obj.event_id)
    if event_obj == None:
        raise HTTPException(status_code=404, detail="Event not found")

    studio_dict = studio.Studio.find_by_id(
        c.db[studio.Studio.COLLECTION_NAME], event_obj.studio_id)
    if studio_dict == None:
        raise HTTPException(status_code=404, detail="Studio not found")

    return FileResponse(file_obj.build_path(c.studios_dir.joinpath(studio_dict['dir_name']).joinpath(event_obj.directory_name)))

    """


@app.post("/studios/{dir_name}/import/")
async def import_studio(dir_name: str) -> StudiosResponse:

    # make sure this studio doesn't already exist
    if c.db[studios.Studios.COLLECTION_NAME].find_one({"dir_name": dir_name}):
        raise HTTPException(status_code=400, detail="Studio already exists")

    # make sure the dir already exists
    if not studios.Studios.DIR.joinpath(dir_name).exists():
        raise HTTPException(
            status_code=404, detail="Studio directory not found")

    new_studio = studio.Studio(
        _id=studio.Studio.generate_id(), dir_name=dir_name)
    new_studio.insert(c.db[studios.Studios.COLLECTION_NAME])

    return await get_studios()


@app.post("/studios/{studio_id}/delete/")
async def delete_studio(studio_id: types.StudioId) -> StudiosResponse:

    if not studio.Studio.exists(c.db[studios.Studios.COLLECTION_NAME], studio_id):
        raise HTTPException(status_code=404, detail="Studio not found")

    studio.Studio.delete_by_id(
        c.db[studios.Studios.COLLECTION_NAME], studio_id)
    return await get_studios()


class StudioResponse(typing.TypedDict):
    studio: studio.Studio
    events: events.Events.PluralByIdType
    event_dir_names_to_add: set[str]
    event_ids_to_delete: set[types.EventId]


@app.get("/studio/{studio_id}/")
async def get_studio(studio_id: types.StudioId) -> StudioResponse:

    given_studio = studio.Studio.find_by_id(
        c.db[studios.Studios.COLLECTION_NAME], studio_id)

    if given_studio == None:
        raise HTTPException(status_code=404, detail="Studio not found")

    d: StudioResponse = {}
    d['studio'] = given_studio
    d['events'] = events.Events.find(
        c.db[events.Events.COLLECTION_NAME], {'studio_id': studio_id})
    return d
"""

    if __name__ == "__main__":
        uvicorn.run("app:app", port=c.uvicorn_port, reload=True)
