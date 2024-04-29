from pymongo import database, collection, MongoClient
from src import types
import pydantic
import datetime as datetime_module


class Event(types.Event):

    _IMAGES_KEY: str = 'images'
    date: datetime_module.date = pydantic.Field(
        default=None, exclude=True)
    name: str = pydantic.Field(default=None, exclude=True)

    def model_post_init(self, _):
        """Set the id from the datetime and name."""

        date_str, self.name = self.id.split(' ', 1)
        self.date = datetime_module.date.fromisoformat(date_str)

    def get_image_group_ids(self, db_events: database.Database) -> list[types.ImageGroupId]:
        """returns a list of all image group ids in the event"""

        document = self.get_collection(db_events).find_one()
        return document[self._IMAGES_KEY].keys()

    def get_collection(self, db_events: database.Database) -> collection.Collection:
        """returns a collection from the events database by event_id"""
        return db_events.get_collection(self.id)


class Events:

    DB_KEY = 'events'

    @staticmethod
    def get_db(mongo_client: MongoClient) -> database.Database:
        """returns the events database"""
        return mongo_client.get_database(Events.DB_KEY)

    @staticmethod
    def get_db_event_ids(db_events: database.Database) -> list[types.EventId]:
        """returns a list of all collections in the events database"""
        return db_events.list_collection_names()
