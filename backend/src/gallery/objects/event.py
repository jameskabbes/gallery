from pymongo import database, collection, MongoClient
from gallery import types, utils
from gallery.objects.bases.document_object import DocumentObject
from gallery.objects.media.image import group, size
from gallery.objects.media import media
import pydantic
import datetime as datetime_module
from pathlib import Path
import typing


class Types:
    id = types.EventId
    datetime = datetime_module.datetime
    name = str
    media = media.Media


class Init:
    id = Types.id
    datetime = Types.datetime | None
    name = Types.name
    media = Types.media


class Model(DocumentObject[Init.id]):
    datetime: Init.datetime = pydantic.Field(
        default=None)
    name: Init.name = pydantic.Field(default=None)
    media: Init.media = pydantic.Field(default_factory=media.Media)

    class Config:
        _DIRECTORY_NAME_DELIM: str = ' '
        _DATE_FILENAME_FORMAT: str = '%Y-%m-%d'

        class DirectoryNameContents(typing.TypedDict):
            datetime: Init.datetime
            name: Init.name


class Event(Model):

    @property
    def directory_name(self) -> str:
        return self.build_directory_name({'date': self.datetime, 'name': self.name})

    @staticmethod
    def parse_directory_name(directory_name: str) -> Model.Config.DirectoryNameContents:
        """Split the directory name into its defining keys."""
        args = directory_name.split(
            Model.Config._DIRECTORY_NAME_DELIM, 1)

        try:
            datetime = datetime_module.datetime.strptime(
                args[0], Model.Config._DATE_FILENAME_FORMAT)
            name = args[1]
        except:
            datetime = None
            name = directory_name

        return {'datetime': datetime, 'name': name}

    @staticmethod
    def build_directory_name(d: Model.Config.DirectoryNameContents) -> str:

        directory_name = ''
        if d['datetime'] != None:
            directory_name += d['datetime'].strftime(
                Model.Config._DATE_FILENAME_FORMAT)
            directory_name += Model.Config._DIRECTORY_NAME_DELIM
        directory_name += d['name']
        return directory_name

    @classmethod
    def find_by_datetime_and_name(cls, collection: collection.Collection, d: Model.Config.DirectoryNameContents) -> typing.Self | None:

        result = collection.find_one(d)
        if result is None:
            return None
        return cls(**result)

    @classmethod
    def load_by_directory(cls, collection: collection.Collection, directory: Path) -> typing.Self:

        datetime_and_name = Event.parse_directory_name(directory.name)
        event = Event.find_by_datetime_and_name(collection, datetime_and_name)

        if event is None:
            event = Event(_id=cls.generate_id(), **datetime_and_name)
            event.insert(collection)

        # get all files in directry
        for file in directory.iterdir():
            if file.is_file():
                print(file)

                # add it to media
                media_file = None
