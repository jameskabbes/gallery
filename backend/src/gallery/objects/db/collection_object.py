import typing
from pymongo import collection, database, results
from gallery.objects.db import document_object
from gallery import types, config
import pathlib
from abc import ABC, abstractmethod


class CollectionObject[DocumentIdType: types.DocumentId, DocumentType: document_object.DocumentObject](ABC):

    COLLECTION_NAME: typing.ClassVar[str]
    CHILD_DOCUMENT_CLASS: typing.ClassVar[document_object.DocumentObject] = document_object.DocumentObject
    PluralByIdType: typing.ClassVar = dict[DocumentIdType, DocumentType]

    @classmethod
    def delete_by_ids(cls, collection: collection.Collection, ids: set[DocumentIdType]) -> results.DeleteResult:
        return collection.delete_many({cls.CHILD_DOCUMENT_CLASS.ID_KEY: {'$in': list(ids)}})

    @ classmethod
    def get_collection(cls, database: database.Database) -> collection.Collection:
        return database[cls.COLLECTION_NAME]

    @ classmethod
    def get(cls, collection: collection.Collection, filter: dict = {}, projection: dict = {}) -> list[typing.Self]:
        return [cls.CHILD_DOCUMENT_CLASS(**i) for i in collection.find(filter, projection=projection)]

    @ classmethod
    def find_ids(cls, collection: collection.Collection, filter: dict = {}) -> set[DocumentIdType]:
        return {i[cls.CHILD_DOCUMENT_CLASS.ID_KEY] for i in collection.find(filter, projection={cls.CHILD_DOCUMENT_CLASS.ID_KEY: 1})}

    # @ classmethod
    # def find_empty_ids(cls, collection: collection.Collection) -> set[DocumentIdType]:
    #     """find ids that have no document associated with them in the collection."""

    #     return {i[config.DOCUMENT_ID_KEY] for i in collection.find(filter, projection={config.DOCUMENT_ID_KEY: 1}) if not i}
