from gallery import types, config, utils
from gallery.objects import studio as studio_module, events as events_module
from gallery.objects.db import collection_object
import typing
import pydantic
import pathlib
from pymongo import collection as pymongo_collection


class Studios(pydantic.BaseModel, collection_object.CollectionObject[types.StudioId, studio_module.Studio]):
    COLLECTION_NAME: typing.ClassVar[str] = 'studios'
    CHILD_DOCUMENT_CLASS: typing.ClassVar = studio_module.Studio
    PluralByIdType: typing.ClassVar = dict[types.StudioId,
                                           studio_module.Studio]

    studios: dict[types.StudioId, studio_module.Studio] = pydantic.Field(
        default_factory=dict)

    @classmethod
    def find_to_add_and_delete(cls, collection: pymongo_collection.Collection, dir: pathlib.Path):

        local_id_keys: set[tuple[studio_module.Types.ID_TYPES]] = set()
        for subdir in dir.iterdir():
            if subdir.is_dir():
                d = studio_module.Studio.parse_directory_name(subdir.name)
                local_id_keys.add(tuple(d[k]
                                        for k in studio_module.Types.ID_KEYS))

        # ids and id_keys in the database
        db_id_and_id_keys = collection.find(projection={
            ID_KEY: 1 for ID_KEY in studio_module.Types.ID_KEYS})

        # { ('studio1',): 'sjk320sjk3' }
        db_id_by_id_keys: dict[tuple[studio_module.Types.ID_TYPES],
                               types.StudioId] = {}

        for item in db_id_and_id_keys:
            id_keys_tuple = tuple(
                item[k] for k in studio_module.Types.ID_KEYS)
            if id_keys_tuple in db_id_by_id_keys:
                raise ValueError(
                    f"Duplicate keys in db: {cls.CHILD_DOCUMENT_CLASS.IDENTIFYING_KEYS}={id_keys_tuple}")
            db_id_by_id_keys[id_keys_tuple] = item[studio_module.Studio.ID_KEY]

        db_id_keys = set(db_id_by_id_keys.keys())

        id_keys_to_add = local_id_keys - db_id_keys
        id_keys_to_remove = db_id_keys - local_id_keys
        ids_to_remove = set([db_id_by_id_keys[id_keys]
                             for id_keys in id_keys_to_remove])

        return id_keys_to_add, ids_to_remove
