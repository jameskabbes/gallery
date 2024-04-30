from pymongo import database, collection, MongoClient


class Base:

    DATABASE_ID: str

    @staticmethod
    def get_db(mongo_client: MongoClient) -> database.Database:
        """returns the database"""
        return mongo_client.get_database(Base.DATABASE_ID)
