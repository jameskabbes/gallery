from gallery import types
from gallery.objects.media.image import file as image_file, version as image_version
from gallery.objects.media.bases import group as base_group
from gallery.objects.bases.document_object import DocumentObject
import pydantic
import datetime as datetime_module


class Model(DocumentObject[types.VideoGroupId], base_group.Group[image_version.Version]):
    pass


class Group(Model):

    class Config:
        COLLECTION_NAME = 'image_groups'
        ACCEPTABLE_FILE_ENDINGS = {'jpg', 'jpeg', 'png', 'gif', 'cr2',
                                   'bmp', 'tiff', 'tif', 'ico', 'svg', 'webp', 'raw', 'heif', 'heic'}
