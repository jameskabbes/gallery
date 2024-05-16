from gallery import types
import pydantic
import typing
from abc import ABC, abstractmethod

from gallery.objects.bases import document_object
from gallery import types
import pathlib


class Types:
    media_type = types.MediaType
    event_id = str
    name = str
    file_ending = types.FileEnding
    relative_path = str

    ID_TYPES = typing.Literal['media_type', 'event_id',
                              'name', 'file_ending', 'relative_path']
    ID_KEYS = ('media_type', 'event_id', 'name',
               'file_ending', 'relative_path')


class Base:
    _VERSION_DELIM: typing.ClassVar[str] = '-'
    _SIZE_BEG_TRIGGER: typing.ClassVar[str] = '('
    _SIZE_END_TRIGGER: typing.ClassVar[str] = ')'

    FILENAME_IO_KEYS: typing.ClassVar
    FilenameIODict = typing.TypedDict('FilenameIODict', {
    })


class File(Base, document_object.DocumentObject[types.MediaId, Types.ID_TYPES], ABC):
    media_type: Types.media_type
    event_id: Types.event_id
    name: Types.name
    file_ending: Types.file_ending
    relative_path: Types.relative_path
    ACCEPTABLE_FILE_ENDINGS: typing.ClassVar[types.AcceptableFileEndings] = {}
    COLLECTION_NAME: typing.ClassVar[str] = 'media'

    @property
    def filename(self):
        return self.build_filename(
            {k: getattr(self, k) for k in self.FILENAME_IO_KEYS}
        )

    @classmethod
    @abstractmethod
    def parse_filename(cls, filename: types.Filename):
        """ Parse the filename into its defining keys."""

    @classmethod
    @abstractmethod
    def build_filename(cls, i_o_dict: dict) -> types.Filename:
        """ Build the filename from the defining keys."""

    def build_path(self, event_dir: pathlib.Path):
        return event_dir / pathlib.Path(self.relative_path) / self.filename
