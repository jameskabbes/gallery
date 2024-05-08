import typing
from pathlib import Path
from gallery import config, utils, types
from pymongo import MongoClient, database
from gallery.objects.db import collection_object, document_object
import pydantic


class Types:
    dir_name = str


class Studio(document_object.DocumentObject[types.StudioId]):
    name: str | None = pydantic.Field(default=None)
