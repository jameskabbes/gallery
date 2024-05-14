from gallery import types, config
import pydantic
import re
import datetime as datetime_module
from gallery.objects.media_types.bases import file as base_file
from gallery.objects.db import document_object
import typing


class Types:
    datetime: datetime_module.datetime
    name: str
    ALL_TYPES = typing.Literal['datetime', 'name', 'versions']
    ID_TYPES = typing.Literal['media_type', 'event_id',
                              'name', 'file_ending', 'name', 'datetime']
    ID_KEYS = ('media_type', 'event_id', 'name', 'file_ending')


class Base:
    Basics = dict[str, set[types.FileEnding]]
    FilenameIODict = typing.TypedDict('FilenameIODict', {
        'name': str,
        'file_ending': types.FileEnding
    })


class File(Base, document_object.DocumentObject[types.VideoFileId, Types.ID_KEYS], base_file.File):
    datetime: datetime_module.datetime | None = pydantic.Field(default=None)
    name: str

    ACCEPTABLE_FILE_ENDINGS: typing.ClassVar[types.AcceptableFileEndings] = {'mp4', 'mkv', 'flv', 'avi',
                                                                             'mov', 'wmv', 'rm', 'mpg', 'mpeg', '3gp', 'webm', 'vob', 'ogv'}
    IDENTIFYING_KEYS: typing.ClassVar[tuple[Types.ID_TYPES]] = Types.ID_KEYS

    media_type: typing.ClassVar[str] = 'video.file'

    @classmethod
    def parse_filename(cls, filename: types.Filename) -> Base.FilenameIODict:
        """ Parse the filename into its defining keys."""

        d: Base.FilenameIODict = {}
        d['name'], d['file_ending'] = filename.split('.', 1)
        return d

    @classmethod
    def build_filename(cls, i_o_dict: Base.FilenameIODict) -> types.Filename:
        """ Build the filename from the defining keys."""

        return '{}.{}'.format(i_o_dict['name'], i_o_dict['file_ending'])

    @classmethod
    def load_basic_by_filenames(cls, filenames: list[types.Filename]) -> Base.Basics:

        basic_by_filename: Base.Basics = {}

        for filename in filenames:
            file_io_dict = cls.parse_filename(filename)

            if file_io_dict['name'] not in basic_by_filename:
                basic_by_filename[file_io_dict['name']] = set()

            basic_by_filename[file_io_dict['name']].add(
                file_io_dict['file_ending'])

        return basic_by_filename
