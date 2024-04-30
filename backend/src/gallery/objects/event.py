from pymongo import database, collection, MongoClient
from src import types, databases
import pydantic
import datetime as datetime_module


class Event(pydantic.BaseModel):

    id: types.EventId
    date: datetime_module.date = pydantic.Field(
        default=None, exclude=True)
    name: str = pydantic.Field(default=None, exclude=True)

    class Config:
        _IMAGES_KEY: str = 'images'

    def model_post_init(self, _):
        """Set the id from the datetime and name."""

        items = self.id.split(' ', 1)
        if len(items) > 1:
            self.name = items[-1]
            try:
                self.date = datetime_module.date.fromisoformat(items[0])
            except:
                self.date = datetime_module.date.max
        else:
            self.name = self.id
            self.date = datetime_module.date.max

    def get_image_groups(self, db_images: databases.images.Database):
        """Returns a list of image group ids for this event."""

        coll = db_images.get_collection(self.id)
        documents = coll.find()


class Events:
    @staticmethod
    def get_event_ids(collection_events: collection.Collection) -> set[types.EventId]:
        """Returns a set of event ids."""
        return set([item['_id'] for item in collection_events.find({}, {'_id': 1})])
