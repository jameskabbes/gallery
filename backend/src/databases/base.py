from pymongo import database, collection, MongoClient
import typing


T = typing.TypeVar('T')


class Database:

    db: database.Database
    DATABASE_ID: str
    COLLECTION_ID: T

    def __init__(self, mongo_client: MongoClient):
        self.db = self.get_db(mongo_client)

    def get_collections(self) -> list[T]:
        return self.db.list_collection_names()

    @staticmethod
    def get_db(mongo_client: MongoClient) -> database.Database:
        """returns the database"""
        return mongo_client.get_database(Database.DATABASE_ID)
