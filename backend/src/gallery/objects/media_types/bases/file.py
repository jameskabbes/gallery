from gallery import types
import pydantic
import typing
from abc import ABC, abstractmethod

from gallery.objects.db import document_object
from gallery import types


class Types:
    media_type = types.MediaCoreType
    event_id = str
    name = str
    file_ending = types.FileEnding

    ID_TYPES = typing.Literal['media_type', 'event_id', 'name', 'file_ending']
    ID_KEYS = ('media_type', 'event_id', 'name', 'file_ending')


class File(document_object.DocumentObject[types.MediaId, Types.ID_TYPES], ABC):
    media_type: Types.media_type
    event_id: Types.event_id
    name: Types.name
    file_ending: Types.file_ending
    ACCEPTABLE_FILE_ENDINGS: typing.ClassVar[types.AcceptableFileEndings] = {}
    COLLECTION_NAME: typing.ClassVar[str] = 'files'

    @classmethod
    @abstractmethod
    def parse_filename(cls, filename: types.Filename):
        """ Parse the filename into its defining keys."""

    @classmethod
    @abstractmethod
    def build_filename(cls, i_o_dict: dict) -> types.Filename:
        """ Build the filename from the defining keys."""
