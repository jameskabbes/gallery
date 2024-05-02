from gallery import types
from gallery.objects.media.image import file, version
from gallery.objects.media.bases import group as base_group
from gallery.objects.bases.document_object import DocumentObject
import pydantic
import datetime as datetime_module


class Model(DocumentObject[types.ImageGroupId], base_group.Group):

    @pydantic.field_validator('name')
    def validate_name(cls, v: str):
        if v.endswith(file.File.Config._SIZE_BEG_TRIGGER):
            raise ValueError('`name` must not end with "{}"'.format(
                file.File.Config._SIZE_END_TRIGGER))
        if file.File.Config._VERSION_DELIM in v:
            raise ValueError('`name` must not contain "{}"'.format(
                file.File.Config._VERSION_DELIM))
        return v


class Group(Model):

    class Config:
        COLLECTION_NAME = 'image_groups'
        ACCEPTABLE_FILE_ENDINGS = {'jpg', 'jpeg', 'png', 'gif', 'cr2',
                                   'bmp', 'tiff', 'tif', 'ico', 'svg', 'webp', 'raw', 'heif', 'heic'}
