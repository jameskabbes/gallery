from fastapi import HTTPException, status
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pymongo import MongoClient, collection as pymongo_collection
from gallery import config, types, utils
from gallery.objects import media, studio, event, client, media_types
from gallery.objects.bases import document_object, collection_object

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

# Studios


def test[T1, T2](a: T1, b: T2) -> dict[T1, T2]:
    return a + b


a: int = 1
b: int = 2

result = test(a, b)


def delete_record[IdType: types.DocumentId, ItemType: collection_object.CollectionObject](id: IdType, collection_object_class: typing.Type[ItemType]):

    result = collection_object_class.delete_by_id(
        c.db[collection_object_class.COLLECTION_NAME], id)
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")

    return {"message": "Record deleted successfully"}


def get_records[IdType: types.DocumentId, ItemType: document_object.DocumentObject](_: IdType, document_object_class: typing.Type[ItemType]) -> dict[IdType, ItemType]:
    return document_object_class.get_all(c.db[document_object_class.COLLECTION_NAME])


def test2() -> types.StudioId:
    return '123'


c1: types.StudioId['123']
d = get_records(c1, studio.Studio)


@app.delete("/studios/{studio_id}")
async def delete_studio(studio_id: types.StudioId):
    return await delete_record(studio_id, studio.Studio)


@app.get("/studios")
async def get_studios() -> dict[types.StudioId, studio.Studio]:
    asdf: types.StudioId
    e = get_records(asdf, studio.Studio)


class StudiosPageResponse(typing.TypedDict):
    studios: dict[types.StudioId, studio.Studio]
    studios_to_add: dict[types.StudioId, studio.Studio]
    studio_ids_to_delete: dict[types.StudioId, None]


@app.get("/studios/page")
async def get_studios_page() -> StudiosPageResponse:
    studio_id_keys_to_add, studios_ids_to_delete = studio.Studio.find_to_add_and_delete(
        c.db[studio.Studio.COLLECTION_NAME], c.studios_dir)

    studios_to_add = {}
    for studio_id_keys in studio_id_keys_to_add:
        studio_inst = studio.Studio.make_from_id_keys(studio_id_keys)
        studios_to_add[studio_inst.id] = studio_inst

    d: StudiosPageResponse = {}
    d['studios'] = await get_studios()
    d['studios_to_add'] = studios_to_add
    d['studio_ids_to_delete'] = {
        studio_id: None for studio_id in studios_ids_to_delete}

    return d

# Studio


@app.get("/studios/{studio_id}")
async def get_studio(studio_id: types.StudioId) -> studio.Studio:

    studio_inst = studio.Studio.get_by_id(
        c.db[studio.Studio.COLLECTION_NAME], studio_id)
    if studio_inst == None:
        raise HTTPException(status_code=404, detail="Studio not found")
    return studio_inst


@app.post("/studios")
async def post_studio(given_studio: studio.Studio):

    if studio.Studio.id_exists(c.db[studio.Studio.COLLECTION_NAME], given_studio.id):
        raise HTTPException(status_code=400, detail="Studio already exists")

    result = given_studio.insert(c.db[studio.Studio.COLLECTION_NAME])

    # make sure this was successful
    if result.inserted_id == None:
        raise HTTPException(
            status_code=500, detail="Failed to insert studio into database")


class StudioPageResponse(typing.TypedDict):
    studio: studio.Studio
    events: dict[types.EventId, event.Event]
    events_to_add: dict[types.EventId, event.Event]
    event_ids_to_delete: dict[types.EventId, None]


@app.get('/studios/{studio_id}/page')
async def get_studio_page(studio_id: types.StudioId) -> StudioPageResponse:

    studio_inst = studio.Studio.get_by_id(
        c.db[studio.Studio.COLLECTION_NAME], studio_id)

    if studio_inst == None:
        raise HTTPException(status_code=404, detail="Studio not found")

    events = event.Event.get(
        c.db[event.Event.COLLECTION_NAME], {'studio_id': studio_id})
    event_id_keys_to_add, event_ids_to_delete = event.Event.find_to_add_and_delete(
        c.db[event.Event.COLLECTION_NAME], c.studios_dir.joinpath(studio_inst.dir_name), studio_id)

    events_to_add = {}
    for event_id_keys in event_id_keys_to_add:
        event_inst = event.Event.make_from_id_keys(event_id_keys)
        events_to_add[event_inst.id] = event_inst

    d: StudioPageResponse = {}
    d['studio'] = studio_inst
    d['events'] = events
    d['events_to_add'] = events_to_add
    d['event_ids_to_delete'] = {
        event_id: None for event_id in event_ids_to_delete}

    return d


# Events

@app.get("studios/{studio_id}/events")
async def get_studio_events(studio_id: types.StudioId) -> dict[types.EventId, event.Event]:
    return event.Event.get_all(c.db[event.Event.COLLECTION_NAME], {'studio_id': studio_id})


@app.post("/events")
async def post_event(given_event: event.Event):

    if event.Event.id_exists(c.db[event.Event.COLLECTION_NAME], given_event.id):
        raise HTTPException(status_code=400, detail="Event already exists")

    result = given_event.insert(c.db[event.Event.COLLECTION_NAME])

    # make sure this was successful
    if result.inserted_id == None:
        raise HTTPException(
            status_code=500, detail="Failed to insert event into database")


@app.delete("/events/{event_id}")
async def delete_event(event_id: types.EventId):
    # Query the database to delete the studio
    result = event.Event.delete_by_id(
        c.db[event.Event.COLLECTION_NAME], event_id)

    # Check if a studio was actually deleted
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    # Return a message indicating the deletion was successful
    return {"message": "Studio deleted successfully"}


class EventResponse(typing.TypedDict):
    event: event.Event
    medias: dict[types.MediaIdType, media_types.FILE_CLASS_TYPE]
    medias_to_add: dict[types.MediaIdType, media_types.FILE_CLASS_TYPE]
    media_ids_to_delete: dict[types.MediaIdType, None]


@app.get('/events/{event_id}')
async def event_page(event_id: types.EventId) -> EventResponse:

    event_inst = event.Event.get_by_id(
        c.db[event.Event.COLLECTION_NAME], event_id)

    if event_inst == None:
        raise HTTPException(status_code=404, detail="Event not found")

    studio_inst = studio.Studio.get_by_id(
        c.db[studio.Studio.COLLECTION_NAME], event_inst.studio_id)

    if studio_inst == None:
        raise HTTPException(
            status_code=404, detail="Event Studio Id not found")

    media_id_keys_to_add, media_ids_to_delete = media.Media.find_to_add_and_delete(
        c.db[event.Event.COLLECTION_NAME], c.studios_dir.joinpath(studio_inst.dir_name).joinpath(event_inst.directory_name), event_id)

    medias = media.Media.get(c.db[media.Media.COLLECTION_NAME], {
                             'event_id': event_id})
    medias_to_add = {}
    for media_id_keys in media_id_keys_to_add:
        media_type = media.Media.get_media_type_from_id_keys(media_id_keys)
        if media_type not in media_types.TYPES:
            continue

        file_class: media_types.FILE_CLASS_TYPE = media_types.FILE_CLASS_MAPPING[media_type]
        media_inst = file_class.make_from_id_keys(
            media_id_keys)
        medias_to_add[media_inst.id] = media_inst

    d: EventResponse = {}
    d['event'] = event_inst
    d['medias'] = medias
    d['medias_to_add'] = medias_to_add
    d['media_ids_to_delete'] = {
        media_id: None for media_id in media_ids_to_delete}

    return d

# Media

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


@ app.get('/file/{file_id}/content')
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
