from pymongo import database, collection, MongoClient
from gallery import types
from gallery.objects.db import document_object
from gallery.objects import media as media_module
import pydantic
import datetime as datetime_module
from pathlib import Path
import typing


class Types:
    datetime = datetime_module.datetime | None
    name = str
    studio_id = types.StudioId
    ALL_TYPES = typing.Literal['datetime', 'name', 'studio_id']
    ID_TYPES = typing.Literal['datetime', 'name', 'studio_id']
    ID_KEYS = ('datetime', 'name', 'studio_id')


class Base:
    DirectoryNameContents: typing.ClassVar = typing.TypedDict('DirectoryNameContents', {
        'datetime': Types.datetime,
        'name': Types.name
    })


class Event(Base, document_object.DocumentObject[types.EventId, Types.ID_TYPES]):
    studio_id: Types.studio_id
    datetime: Types.datetime = pydantic.Field(
        default=None)
    name: Types.name = pydantic.Field(default=None)
    # media: media_module.Media = pydantic.Field(
    #     default_factory=media_module.Media)

    IDENTIFYING_KEYS: typing.ClassVar[tuple[Types.ID_TYPES]] = Types.ID_KEYS

    _DIRECTORY_NAME_DELIM: typing.ClassVar[str] = ' '
    _DATE_FILENAME_FORMAT: typing.ClassVar[str] = '%Y-%m-%d'

    @property
    def directory_name(self) -> str:
        return self.build_directory_name({'datetime': self.datetime, 'name': self.name})

    @classmethod
    def parse_directory_name(cls, dir_name: str) -> Base.DirectoryNameContents:
        args = dir_name.split(
            Event._DIRECTORY_NAME_DELIM, 1)

        d: Base.DirectoryNameContents = {'datetime': None}

        try:
            datetime = datetime_module.datetime.strptime(
                args[0], Event._DATE_FILENAME_FORMAT)
            d['name'] = args[1]
            d['datetime'] = datetime
        except:
            d['name'] = dir_name

        return d

    @classmethod
    def build_directory_name(cls, d: Base.DirectoryNameContents) -> str:

        directory_name = ''
        if d['datetime'] != None:
            directory_name += d['datetime'].strftime(
                cls._DATE_FILENAME_FORMAT)
            directory_name += cls._DIRECTORY_NAME_DELIM
        directory_name += d['name']
        return directory_name

    @classmethod
    def load_by_directory(cls, db: database.Database, directory: Path) -> typing.Self:

        # get datetime and name from directory name
        datetime_and_name = Event.parse_directory_name(directory.name)

        # # find event in the db collection
        event_collection = db[cls.COLLECTION_NAME]
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
            event.insert(db[cls.COLLECTION_NAME])
        elif 'new_media' in update_modes:
            print('update event media')
            event.update_fields(
                db[cls.COLLECTION_NAME], {'media', })
