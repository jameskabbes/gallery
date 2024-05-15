import typing
from pathlib import Path
from gallery import config, utils, types
from pymongo import MongoClient, database, collection as pymongo_collection
from gallery.objects.db import document_object
import pydantic
import pathlib


class Types:
    dir_name = str
    name = str
    ALL_TYPES = typing.Literal['dir_name', 'name']
    ID_TYPES = typing.Literal['dir_name']
    ID_KEYS = ('dir_name',)


class Base:
    DirectoryNameContents: typing.ClassVar = typing.TypedDict('DirectoryNameContents', {
        'dir_name': Types.dir_name,
    })


class Studio(Base, document_object.DocumentObject[types.StudioId, Types.ID_TYPES]):
    dir_name: Types.dir_name
    name: Types.name | None = pydantic.Field(default=None)
    IDENTIFYING_KEYS: typing.ClassVar[tuple[Types.ID_TYPES]] = Types.ID_KEYS
    COLLECTION_NAME: typing.ClassVar[str] = 'studios'

    @classmethod
    def parse_directory_name(cls, dir_name: str) -> Base.DirectoryNameContents:
        return {'dir_name': dir_name}

    @classmethod
    def build_directory_name(cls, d: Base.DirectoryNameContents) -> str:
        return d['dir_name']

    @classmethod
    def find_to_add_and_delete(cls, collection: pymongo_collection.Collection, dir: pathlib.Path) -> tuple[set[tuple[Types.ID_TYPES]], set[types.StudioId]]:

        local_id_keys: set[tuple[Types.ID_TYPES]] = set()
        for subdir in dir.iterdir():
            if subdir.is_dir():
                d = cls.parse_directory_name(subdir.name)
                local_id_keys.add(cls.dict_id_keys_to_tuple(d))

        db_id_by_id_keys = cls.find_id_by_id_keys(collection)
        db_id_keys = set(db_id_by_id_keys.keys())

        id_keys_to_add = local_id_keys - db_id_keys
        id_keys_to_remove = db_id_keys - local_id_keys
        ids_to_remove = set([db_id_by_id_keys[id_keys]
                             for id_keys in id_keys_to_remove])

        return id_keys_to_add, ids_to_remove
