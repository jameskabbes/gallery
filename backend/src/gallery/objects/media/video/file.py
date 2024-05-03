from gallery import types, config
import pydantic
import re
import datetime as datetime_module
from gallery.objects.media.bases import file as base_file
from gallery.objects.bases.document_object import DocumentObject
from gallery.objects.media.bases import content_loader
import typing


class Base:
    Basics = dict[str, set[types.FileEnding]]
    FilenameIODict = typing.TypedDict('FilenameIODict', {
        'file_root': str,
        'file_ending': types.FileEnding
    })


class File(Base, DocumentObject[types.VideoId], base_file.File):

    event_id: types.EventId
    datetime: datetime_module.datetime | None = pydantic.Field(default=None)
    name: str

    COLLECTION_NAME: typing.ClassVar[str] = 'video_files'
    ACCEPTABLE_FILE_ENDINGS: typing.ClassVar[types.AcceptableFileEndings] = {'mp4', 'mkv', 'flv', 'avi',
                                                                             'mov', 'wmv', 'rm', 'mpg', 'mpeg', '3gp', 'webm', 'vob', 'ogv'}

    @classmethod
    def parse_filename(cls, filename: types.Filename) -> Base.FilenameIODict:
        """ Parse the filename into its defining keys."""

        d: Base.FilenameIODict = {}
        d['file_root'], d['file_ending'] = filename.split('.', 1)
        return d

    @classmethod
    def build_filename(cls, i_o_dict: Base.FilenameIODict) -> types.Filename:
        """ Build the filename from the defining keys."""

        return '{}.{}'.format(i_o_dict['file_root'], i_o_dict['file_ending'])

    @classmethod
    def load_basic_by_filenames(cls, filenames: list[types.Filename]) -> Base.Basics:

        basic_by_filename: Base.Basics = {}

        for filename in filenames:
            file_io_dict = cls.parse_filename(filename)

            if file_io_dict['file_root'] not in basic_by_filename:
                basic_by_filename[file_io_dict['file_root']] = set()

            basic_by_filename[file_io_dict['file_root']].add(
                file_io_dict['file_ending'])

        return basic_by_filename
