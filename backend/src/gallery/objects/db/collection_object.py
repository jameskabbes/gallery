import typing
from pymongo import collection, database
from gallery.objects.db import document_object
from gallery import types


class CollectionObject[DocumentType: document_object.DocumentObject, DocumentIdType: types.DocumentId]:

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
