from gallery import types, config
import pydantic
import re
import datetime as datetime_module
from gallery.objects.media.bases import file as base_file
import typing
from gallery.objects.bases.document_object import DocumentObject


class Base:
    pass


class File(Base, DocumentObject[types.VideoId], base_file.File):

    event_id: types.EventId
    datetime: datetime_module.datetime | None = pydantic.Field(default=None)
    name: str

    COLLECTION_NAME: typing.ClassVar[str] = 'video_files'
    ACCEPTABLE_FILE_ENDINGS: typing.ClassVar[types.AcceptableFileEndings] = {'mp4', 'mkv', 'flv', 'avi',
                                                                             'mov', 'wmv', 'rm', 'mpg', 'mpeg', '3gp', 'webm', 'vob', 'ogv'}
