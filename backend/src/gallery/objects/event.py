from pymongo import database, collection, MongoClient
from gallery import types
from gallery.objects.media.image import group, size
from gallery.objects.media import media
import pydantic
import datetime as datetime_module
from pathlib import Path
import typing


class Types:
    id = types.EventId
    date = datetime_module.date
    name = str
    media = media.Media


class Init:
    id = Types.id
    date = Types.date | None
    name = Types.name
    media = Types.media


class Model(pydantic.BaseModel):
    id: Init.id = pydantic.Field(alias='_id')
    date: Init.date = pydantic.Field(
        default=None, exclude=True)
    name: Init.name = pydantic.Field(default=None, exclude=True)
    media: Init.media = pydantic.Field(default_factory=media.Media)

    class Config:
        _DIRECTORY_NAME_DELIM: str = ' '

        class DirectoryNameContents(typing.TypedDict):
            date: Init.date
            name: Init.name


class Event(Model):

    @property
    def directory_name(self) -> str:
        return self.build_directory_name({'date': self.date, 'name': self.name})

    @staticmethod
    def parse_directory_name(directory_name: str) -> Model.Config.DirectoryNameContents:
        """Split the directory name into its defining keys."""
        args = directory_name.split(
            Model.Config._DIRECTORY_NAME_DELIM, 1)

        try:
            date = datetime_module.date.fromisoformat(args[0])
            name = args[1]
        except:
            date = None
            name = directory_name

        return {'date': date, 'name': name}

    @staticmethod
    def build_directory_name(d: Model.Config.DirectoryNameContents) -> str:

        directory_name = ''
        if d['date'] != None:
            directory_name += d['date'].isoformat()
            directory_name += Model.Config._DIRECTORY_NAME_DELIM
        directory_name += d['name']
        return directory_name

    @classmethod
    def load_from_db_collection_by_id(cls, events_collection: collection.Collection, id: Types.id) -> typing.Self:
        return cls(**events_collection.find_one({'_id': id}, {"_id": 1, "date": 1, "name": 1}))
