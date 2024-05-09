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
    def find(cls, collection: collection.Collection, filter: dict = {}, projection: dict = {}) -> dict[DocumentIdType, DocumentType]:
        items = [cls.CHILD_DOCUMENT_CLASS(**i)
                 for i in collection.find(filter, projection=projection)]
        return {item.id: item for item in items}

    @ classmethod
    def get_ids(cls, collection: collection.Collection, filter: dict = {}) -> set[DocumentIdType]:
        return {i[config.DOCUMENT_ID_KEY] for i in collection.find(filter, projection={config.DOCUMENT_ID_KEY: 1})}

    @ classmethod
    def find_empty_ids(cls, collection: collection.Collection) -> set[DocumentIdType]:
        """find ids that have no document associated with them in the collection."""

        return {i[config.DOCUMENT_ID_KEY] for i in collection.find(filter, projection={config.DOCUMENT_ID_KEY: 1}) if not i}
