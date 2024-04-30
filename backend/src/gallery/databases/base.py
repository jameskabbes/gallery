from pymongo import database, collection, MongoClient
import typing


T_COLLECTION_ID = typing.TypeVar('T_COLLECTION_ID')


class Database:

    db: database.Database
    DATABASE_ID: str
    COLLECTION_ID: T_COLLECTION_ID

    def __init__(self, mongo_client: MongoClient):
        self.db = self.get_db(mongo_client, self.DATABASE_ID)

    def get_collection(self, collection_id: T_COLLECTION_ID) -> collection.Collection:
        return self.db.get_collection(collection_id)

    def get_collections(self) -> list[T_COLLECTION_ID]:
        return self.db.list_collection_names()

    @staticmethod
    def get_db(mongo_client: MongoClient, database_id) -> database.Database:
        """returns the pymongo database"""
        return mongo_client.get_database(database_id)
