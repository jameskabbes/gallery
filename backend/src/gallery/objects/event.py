from pymongo import database, collection as pymongo_collection, MongoClient
from gallery import types
from gallery.objects.bases import document_object
import pydantic
import datetime as datetime_module
import pathlib
import typing


class Types:
    datetime = datetime_module.datetime
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
    datetime: Types.datetime | None = pydantic.Field(
        default=None)
    name: Types.name = pydantic.Field(default=None)

    IDENTIFYING_KEYS: typing.ClassVar[tuple[Types.ID_TYPES]] = Types.ID_KEYS
    COLLECTION_NAME: typing.ClassVar[str] = 'events'

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
                args[0], cls._DATE_FILENAME_FORMAT)
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

    @ classmethod
    def find_to_add_and_delete(cls, collection: pymongo_collection.Collection, dir: pathlib.Path, studio_id: types.StudioId) -> tuple[set[tuple[Types.ID_TYPES]], set[types.EventId]]:

        local_id_keys: set[tuple[Types.ID_TYPES]] = set()
        for subdir in dir.iterdir():
            if subdir.is_dir():
                d = cls.parse_directory_name(subdir.name)
                d['studio_id'] = studio_id
                local_id_keys.add(cls.dict_id_keys_to_tuple(d))

        # ids and id_keys in the database
        db_id_by_id_keys = cls.find_id_by_id_keys(
            collection, {'studio_id': studio_id})

        db_id_keys = set(db_id_by_id_keys.keys())

        id_keys_to_add = local_id_keys - db_id_keys
        id_keys_to_remove = db_id_keys - local_id_keys
        ids_to_remove = set([db_id_by_id_keys[id_keys]
                             for id_keys in id_keys_to_remove])

        return id_keys_to_add, ids_to_remove
