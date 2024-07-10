from pymongo import collection as pymongo_collection, database, results
import typing
from gallery import config


class CollectionObject[IdType]:
    ID_KEY: typing.ClassVar[str] = config.DOCUMENT_ID_KEY
    COLLECTION_NAME: typing.ClassVar[str]

    @ classmethod
    def get_collection(cls, database: database.Database) -> pymongo_collection.Collection:
        return database[cls.COLLECTION_NAME]

    @ classmethod
    def delete_by_id(cls, collection: pymongo_collection.Collection, id: IdType) -> results.DeleteResult:
        """Delete a document from the database by its id."""
        return collection.delete_one({cls.ID_KEY: id})

    @classmethod
    def delete_by_ids(cls, collection: pymongo_collection.Collection, ids: set[IdType]) -> results.DeleteResult:
        return collection.delete_many({cls.ID_KEY: {'$in': list(ids)}})

    @classmethod
    def find_by_id(cls, collection: pymongo_collection.Collection, id: IdType, projection: dict = {}) -> dict | None:
        return collection.find_one({cls.ID_KEY: id}, projection=projection)

    @ classmethod
    def find_ids(cls, collection: pymongo_collection.Collection, filter: dict = {}) -> set[IdType]:
        return {i[cls.ID_KEY] for i in collection.find(filter, projection={cls.ID_KEY: 1})}

    @ classmethod
    def id_exists(cls, collection: pymongo_collection.Collection, id: IdType) -> bool:
        """Check if the document's id exists in the database."""
        return collection.find_one({cls.ID_KEY: id}) is not None
