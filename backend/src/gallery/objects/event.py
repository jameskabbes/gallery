from pymongo import database, collection, MongoClient
from gallery import types
from gallery.objects.image import group, file
import pydantic
import datetime as datetime_module
from pathlib import Path


class Event(pydantic.BaseModel):

    id: types.EventId
    date: datetime_module.date = pydantic.Field(
        default=None, exclude=True)
    name: str = pydantic.Field(default=None, exclude=True)

    image_groups: dict[types.ImageGroupId, group.Group] = pydantic.Field(
        default_factory=dict, exclude=True)

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

    def add_image_file(self, image_file: file.File):
        """Add an image file to the event."""
        if image_file.group_id not in self.image_groups:
            self.add_group(group.Group(id=image_file.group_id))
        self.image_groups[image_file.group_id].add_file(image_file)

    def add_group(self, group: group.Group):
        self.image_groups[group.id] = group

    def load_image_groups_from_directory(self, parent_path: Path):

        # load all files from the directory
        path = parent_path / self.id
        image_files = [f for f in path.iterdir() if f.is_file()]
        print(image_files)


class Events:
    @ staticmethod
    def get_event_ids(collection_events: collection.Collection) -> set[types.EventId]:
        """Returns a set of event ids."""
        return set([item['_id'] for item in collection_events.find({}, {'_id': 1})])
