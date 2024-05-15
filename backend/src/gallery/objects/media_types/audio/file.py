from gallery import types, config
import pydantic
import datetime as datetime_module
from gallery.objects.media_types.bases import file as base_file
from gallery.objects.db import document_object
import typing


class Types:
    datetime: datetime_module.datetime

    ID_TYPES = base_file.Types.ID_TYPES
    ID_KEYS = base_file.Types.ID_KEYS


class Base:
    Basics = dict[str, set[types.FileEnding]]
    FilenameIODict = typing.TypedDict('FilenameIODict', {
        'name': str,
        'file_ending': base_file.Types.file_ending
    })


class File(Base, document_object.DocumentObject[types.VideoFileId, Types.ID_KEYS], base_file.File):
    datetime: datetime_module.datetime | None = pydantic.Field(default=None)
    name: str

    ACCEPTABLE_FILE_ENDINGS: typing.ClassVar[types.AcceptableFileEndings] = {
        'mp4', 'mkv', 'flv', 'avi', }

    IDENTIFYING_KEYS: typing.ClassVar[tuple[Types.ID_TYPES]] = Types.ID_KEYS
