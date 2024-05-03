from gallery import types, config
import pydantic
import re
import datetime as datetime_module
from gallery.objects.media.bases import file as base_file

from gallery.objects.bases.document_object import DocumentObject


class Model(DocumentObject[types.VideoId], base_file.File):
    pass


class File(Model):

    _ACCEPTABLE_FILE_ENDINGS = {'mp4', 'mkv', 'flv', 'avi',
                                'mov', 'wmv', 'rm', 'mpg', 'mpeg', '3gp', 'webm', 'vob', 'ogv'}
