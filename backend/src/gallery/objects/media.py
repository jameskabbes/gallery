import pydantic
from gallery import config, types
from gallery.objects.db import document_object
import typing
import pathlib

from pymongo import collection as pymongo_collection


class Types:
    event_id = types.EventId
    ALL_TYPES = typing.Literal['event_id']
    ID_TYPES = typing.Literal['event_id']
    ID_KEYS = ('event_id',)


class Media(document_object.DocumentObject[types.MediaId, Types.ID_TYPES]):
    event_id: Types.event_id
    COLLECTION_NAME: typing.ClassVar[str] = 'medias'

    @classmethod
    def find_media_ids_with_stale_event_ids(cls, collection: pymongo_collection.Collection, event_ids: list[types.EventId]) -> set[types.MediaId]:
        return cls.find_ids(collection, filter={'event_id': {'$nin': event_ids}})

    @classmethod
    def find_to_add_and_delete(cls, collection: pymongo_collection.Collection, dir: pathlib.Path, event_id: types.EventId):

        local_id_keys: set[tuple] = set()
        for file in dir.iterdir():
            if file.is_file():
                print(file)

        return set(), []
