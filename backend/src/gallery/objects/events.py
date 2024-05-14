import typing
from gallery.objects.db import collection_object
from gallery.objects import event as event_module
from gallery import types, config
from pymongo import collection as pymongo_collection
import pathlib


class Events(collection_object.CollectionObject[types.EventId, event_module.Event]):
    COLLECTION_NAME: typing.ClassVar[str] = 'events'
    CHILD_DOCUMENT_CLASS: typing.ClassVar = event_module.Event
    PluralByIdType: typing.ClassVar = dict[types.EventId, event_module.Event]

    @classmethod
    def find_event_ids_with_stale_studio_ids(cls, collection: pymongo_collection.Collection, studio_ids: list[types.StudioId]) -> set[types.EventId]:
        return cls.find_ids(collection, filter={'studio_id': {'$nin': studio_ids}})

    @ classmethod
    def find_to_add_and_delete(cls, collection: pymongo_collection.Collection, dir: pathlib.Path, studio_id: types.StudioId):

        local_id_keys: set[tuple[event_module.Types.ID_TYPES]] = set()
        for subdir in dir.iterdir():
            if subdir.is_dir():
                d = event_module.Event.parse_directory_name(subdir.name)

                id_key_values = []
                for id_key in event_module.Types.ID_KEYS:
                    if id_key in d:
                        id_key_values.append(d[id_key])
                    elif id_key == 'studio_id':
                        id_key_values.append(studio_id)
                local_id_keys.add(tuple(id_key_values))

        # ids and id_keys in the database
        db_id_and_id_keys = collection.find({'studio_id': studio_id}, projection={
            ID_KEY: 1 for ID_KEY in event_module.Types.ID_KEYS})

        # { (datetime.datetime(2023,12,20,0,0,0), 'Event Name'): 'sjk320sjk3' }
        db_id_by_id_keys: dict[tuple[event_module.Types.ID_TYPES],
                               types.EventId] = {}

        for item in db_id_and_id_keys:
            id_keys_tuple = tuple(
                item[k] for k in event_module.Types.ID_KEYS)
            if id_keys_tuple in db_id_by_id_keys:
                raise ValueError(
                    f"Duplicate keys in db: {cls.CHILD_DOCUMENT_CLASS.IDENTIFYING_KEYS}={id_keys_tuple}")
            db_id_by_id_keys[id_keys_tuple] = item[event_module.Event.ID_KEY]

        db_id_keys = set(db_id_by_id_keys.keys())

        id_keys_to_add = local_id_keys - db_id_keys
        id_keys_to_remove = db_id_keys - local_id_keys
        ids_to_remove = set([db_id_by_id_keys[id_keys]
                             for id_keys in id_keys_to_remove])

        return id_keys_to_add, ids_to_remove
