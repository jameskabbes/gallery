import typing
from pathlib import Path
from gallery import config, utils, types
from pymongo import MongoClient, database
from gallery.objects.db import collection_object, document_object
import pydantic


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


class Studio(document_object.DocumentObject[types.StudioId, Types.ID_TYPES]):
    dir_name: Types.dir_name
    name: Types.name | None = pydantic.Field(default=None)
    IDENTIFYING_KEYS: typing.ClassVar[tuple[Types.ID_TYPES]] = Types.ID_KEYS

    @classmethod
    def parse_directory_name(cls, dir_name: str) -> Base.DirectoryNameContents:
        return {'dir_name': dir_name}

    @classmethod
    def buidl_directory_name(cls, d: Base.DirectoryNameContents) -> str:
        return d['dir_name']
