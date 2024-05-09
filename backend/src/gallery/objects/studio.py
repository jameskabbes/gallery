import typing
from pathlib import Path
from gallery import config, utils, types
from pymongo import MongoClient, database
from gallery.objects.db import collection_object, document_object
import pydantic


class Types:
    dir_name = str


class Studio(document_object.DocumentObject[types.StudioId]):
    dir_name: Types.dir_name
    name: str | None = pydantic.Field(default=None)

    IDENTIFYING_KEYS = ('dir_name',)

    @classmethod
    def parse_into_id_keys(cls, dir_name: str) -> tuple:
        """Parse a string into the identifying keys."""
        return (dir_name,)

    @classmethod
    def build_from_id_keys(cls, id_keys: tuple) -> tuple:
        """Build a string from the id keys."""
        return id_keys[0]
