from gallery import types, config, utils
from gallery.objects import studio as studio_module, events as events_module
from gallery.objects.db import collection_object
import typing
import pydantic
import pathlib
from pymongo import collection, database


class Studios(pydantic.BaseModel, collection_object.CollectionObject[types.StudioId, studio_module.Studio]):
    COLLECTION_NAME: typing.ClassVar[str] = 'studios'
    CHILD_DOCUMENT_CLASS: typing.ClassVar = studio_module.Studio
    PluralByIdType: typing.ClassVar = dict[types.StudioId,
                                           studio_module.Studio]

    studios: dict[types.StudioId, studio_module.Studio] = pydantic.Field(
        default_factory=dict)

    @classmethod
    def find_child_document_id_keys_in_dir(cls, dir: pathlib.Path) -> set[tuple]:
        """parse the given directory and return the identifying keys of the child documents."""
        local_ids_keys = set()
        for subdir in dir.iterdir():
            if subdir.is_dir():
                local_ids_keys.add(
                    cls.CHILD_DOCUMENT_CLASS.parse_into_id_keys(subdir.name))
        return local_ids_keys

    @ classmethod
    def sync_db_with_local(cls, collection: collection.Collection, dir: pathlib.Path, nanoid_alphbet: str, nanoid_size: int):

        local_id_keys = cls.find_child_document_id_keys_in_dir(dir)
        print(local_id_keys)

        db_id_and_id_keys = collection.find(projection={
            ID_KEY: 1 for ID_KEY in cls.CHILD_DOCUMENT_CLASS.IDENTIFYING_KEYS})
        print('db_id_and_id_keys:', db_id_and_id_keys)

        # { ('studio1',): 'sjk320sjk3' }
        db_id_by_id_keys: dict[tuple, types.StudioId] = {}
        for item in db_id_and_id_keys:
            id_keys_tuple = tuple(
                item[k] for k in cls.CHILD_DOCUMENT_CLASS.IDENTIFYING_KEYS)
            if id_keys_tuple in db_id_by_id_keys:
                raise ValueError(
                    f"Duplicate keys in db: {cls.CHILD_DOCUMENT_CLASS.IDENTIFYING_KEYS}={id_keys_tuple}")
            db_id_by_id_keys[id_keys_tuple] = item[config.DOCUMENT_ID_KEY]

        print('db_id_by_id_keys:', db_id_by_id_keys)

        db_id_keys = set(db_id_by_id_keys.keys())

        id_keys_to_add = local_id_keys - db_id_keys
        print('ids keys to add:', id_keys_to_add)
        id_keys_to_remove = db_id_keys - local_id_keys
        print('ids keys to remove:', id_keys_to_remove)

        for id_keys in id_keys_to_add:
            print(id_keys)

            construction_dict = {
                config.DOCUMENT_ID_KEY: cls.CHILD_DOCUMENT_CLASS.generate_id(
                    nanoid_alphbet, nanoid_size)
            }
            for id_key in cls.CHILD_DOCUMENT_CLASS.IDENTIFYING_KEYS:
                construction_dict[id_key] = id_keys[cls.CHILD_DOCUMENT_CLASS.IDENTIFYING_KEYS.index(
                    id_key)]

            print(construction_dict)
            new_cls_inst = cls.CHILD_DOCUMENT_CLASS(**construction_dict)
            new_cls_inst.insert(collection)

        for id_keys in id_keys_to_remove:
            cls.CHILD_DOCUMENT_CLASS.delete_by_id(
                collection, db_id_by_id_keys[id_keys])
