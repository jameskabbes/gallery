import typing
from pymongo import collection, database
from gallery.objects.db import document_object
from gallery import types, config
import pathlib
from abc import ABC, abstractmethod


class CollectionObject[DocumentIdType: types.DocumentId, DocumentType: document_object.DocumentObject](ABC):

    COLLECTION_NAME: typing.ClassVar[str]
    CHILD_DOCUMENT_CLASS: typing.ClassVar[document_object.DocumentObject] = document_object.DocumentObject
    PluralByIdType: typing.ClassVar = dict[DocumentIdType, DocumentType]

    @ classmethod
    def get_collection(cls, database: database.Database) -> collection.Collection:
        return database[cls.COLLECTION_NAME]

    @ classmethod
    def get(cls, collection: collection.Collection, filter: dict = {}, projection: dict = {}) -> list[typing.Self]:
        return [cls.CHILD_DOCUMENT_CLASS(**i) for i in collection.find(filter, projection=projection)]

    @ classmethod
    def find(cls, collection: collection.Collection, filter: dict = {}, projection: dict = {}) -> dict[DocumentIdType, DocumentType]:
        return collection.find(filter, projection=projection)

    @ classmethod
    def find_ids(cls, collection: collection.Collection, filter: dict = {}) -> set[DocumentIdType]:
        return {i[config.DOCUMENT_ID_KEY] for i in collection.find(filter, projection={config.DOCUMENT_ID_KEY: 1})}

    # @ classmethod
    # def find_empty_ids(cls, collection: collection.Collection) -> set[DocumentIdType]:
    #     """find ids that have no document associated with them in the collection."""

    #     return {i[config.DOCUMENT_ID_KEY] for i in collection.find(filter, projection={config.DOCUMENT_ID_KEY: 1}) if not i}

    @classmethod
    @abstractmethod
    def find_child_document_id_keys_in_dir(cls, dir: pathlib.Path) -> set[tuple]:
        """parse the given directory and return the identifying keys of the child documents."""
        raise NotImplementedError

    @classmethod
    def get_to_add_and_delete(cls, collection: collection.Collection, dir: pathlib.Path) -> tuple[set[tuple], set[DocumentIdType]]:

        local_id_keys = cls.find_child_document_id_keys_in_dir(dir)

        # ids and id_keys in the database
        db_id_and_id_keys = collection.find(projection={
            ID_KEY: 1 for ID_KEY in cls.CHILD_DOCUMENT_CLASS.IDENTIFYING_KEYS})

        # { ('studio1',): 'sjk320sjk3' }
        db_id_by_id_keys: dict[tuple, DocumentIdType] = {}
        for item in db_id_and_id_keys:
            id_keys_tuple = tuple(
                item[k] for k in cls.CHILD_DOCUMENT_CLASS.IDENTIFYING_KEYS)
            if id_keys_tuple in db_id_by_id_keys:
                raise ValueError(
                    f"Duplicate keys in db: {cls.CHILD_DOCUMENT_CLASS.IDENTIFYING_KEYS}={id_keys_tuple}")
            db_id_by_id_keys[id_keys_tuple] = item[config.DOCUMENT_ID_KEY]

        db_id_keys = set(db_id_by_id_keys.keys())

        id_keys_to_add = local_id_keys - db_id_keys
        id_keys_to_remove = db_id_keys - local_id_keys

        return id_keys_to_add, set([db_id_by_id_keys[id_keys] for id_keys in id_keys_to_remove])
