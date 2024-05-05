import typing
from pymongo import collection, database


class CollectionObject:

    COLLECTION_NAME: typing.ClassVar[str]

    @classmethod
    def get_collection(cls, database: database.Database) -> collection.Collection:
        return database[cls.COLLECTION_NAME]
