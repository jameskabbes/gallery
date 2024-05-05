from pymongo import database, collection, MongoClient
from gallery import types, utils
from gallery.db.document_object import DocumentObject
from gallery.objects.media.image import group
from gallery.objects import media as media_module
from gallery.objects.media.media import Media
import pydantic
import datetime as datetime_module
from pathlib import Path
import typing


class Types:
    datetime = datetime_module.datetime | None
    name = types.ImageGroupName


class Base:
    DirectoryNameContents: typing.ClassVar = typing.TypedDict('DirectoryNameContents', {
        'datetime': Types.datetime,
        'name': Types.name
    })


class Event(Base, DocumentObject[types.EventId]):

    datetime: Types.datetime = pydantic.Field(
        default=None)
    name: Types.name = pydantic.Field(default=None)
    media: Media = pydantic.Field(default_factory=Media)

    COLLECTION_NAME: typing.ClassVar[str] = 'events'
    _DIRECTORY_NAME_DELIM: typing.ClassVar[str] = ' '
    _DATE_FILENAME_FORMAT: typing.ClassVar[str] = '%Y-%m-%d'

    @property
    def directory_name(self) -> str:
        return self.build_directory_name({'date': self.datetime, 'name': self.name})

    @staticmethod
    def parse_directory_name(directory_name: str) -> Base.DirectoryNameContents:
        """Split the directory name into its defining keys."""
        args = directory_name.split(
            Event._DIRECTORY_NAME_DELIM, 1)

        try:
            datetime = datetime_module.datetime.strptime(
                args[0], Event._DATE_FILENAME_FORMAT)
            name = args[1]
        except:
            datetime = None
            name = directory_name

        return {'datetime': datetime, 'name': name}

    @staticmethod
    def build_directory_name(d: Base.DirectoryNameContents) -> str:

        directory_name = ''
        if d['datetime'] != None:
            directory_name += d['datetime'].strftime(
                Event._DATE_FILENAME_FORMAT)
            directory_name += Event._DIRECTORY_NAME_DELIM
        directory_name += d['name']
        return directory_name

    @classmethod
    def find_by_datetime_and_name(cls, collection: collection.Collection, d: Base.DirectoryNameContents) -> typing.Self | None:

        result = collection.find_one(d)
        if result is None:
            return None
        return cls(**result)

    @classmethod
    def load_by_directory(cls, db_collections: types.DbCollections, directory: Path) -> typing.Self:

        # get datetime and name from directory name
        datetime_and_name = Event.parse_directory_name(directory.name)

        # # find event in the db collection
        event_collection = db_collections[cls.COLLECTION_NAME]
        event = Event.find_by_datetime_and_name(
            event_collection, datetime_and_name)

        update_modes = set()

        # create new event if not found
        if event is None:
            event = Event(_id=cls.generate_id(), **datetime_and_name)
            update_modes.add('new_event')

        # split files by media type
        filenames_by_media_type: dict[media_module.KEYS_TYPE,
                                      list[types.Filename]] = {}

        for file in directory.iterdir():
            if file.is_file():
                if not file.suffix.islower():
                    file = file.rename(file.with_suffix(file.suffix.lower()))

                media_type = media_module.get_media_type_by_file_ending(
                    file.suffix[1:])
                if media_type == None:
                    print('Skipping file: not a supported file type')
                    continue

                if media_type not in filenames_by_media_type:
                    filenames_by_media_type[media_type] = []
                filenames_by_media_type[media_type].append(file.name)

        print(filenames_by_media_type)

        # run media importer for each media type
        for media_type in filenames_by_media_type:
            is_new_media_added = event.media.load_basic_by_filenames(
                media_type, filenames_by_media_type[media_type])

            print('-------------')

            if is_new_media_added:
                update_modes.add('new_media')

        # write back to db
        if 'new_event' in update_modes:
            print('writing new event')
            event.insert(db_collections[cls.COLLECTION_NAME])
        elif 'new_media' in update_modes:
            print('update event media')
            event.update_fields(
                db_collections[cls.COLLECTION_NAME], {'media', })
