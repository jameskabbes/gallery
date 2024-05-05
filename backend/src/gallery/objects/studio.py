import typing
from pathlib import Path
from gallery import config, utils, types
from pymongo import MongoClient, database
from gallery.db import collection_object, document_object
import pydantic


class Studio(collection_object.CollectionObject, document_object.DocumentObject):
    DB_NAME: typing.ClassVar[str] = 'studio'
    COLLECTION_NAME: typing.ClassVar[str] = 'studio'
    studio_dir: Path | None = pydantic.Field(default=None)
    _id: str = 'studio'
