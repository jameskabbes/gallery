from pymongo import database, collection, MongoClient
from src import types
import pydantic
import datetime as datetime_module
import collections.abc


class Event(pydantic.BaseModel):

    id: types.EventId
    date: datetime_module.date = pydantic.Field(
        default=None, exclude=True)
    name: str = pydantic.Field(default=None, exclude=True)

    class Config:
        _IMAGES_KEY: str = 'images'

    def model_post_init(self, _):
        """Set the id from the datetime and name."""

        date_str, self.name = self.id.split(' ', 1)
        self.date = datetime_module.date.fromisoformat(date_str)

    def get_image_group_ids(self, event_collection: collection.Collection) -> collections.abc.KeysView[types.ImageGroupId]:
        """returns a all image group ids in the event"""

        # query top level keys from mongodb collection

        document = self.get_collection(db_events).find_one()
        return document[self.Config._IMAGES_KEY].keys()

    def get_collection(self, db_events: database.Database) -> collection.Collection:
        """returns a collection from the events database by event_id"""
        return db_events.get_collection(self.id)
