from gallery import types
from gallery.objects.media.image import size, version
from gallery.objects.bases.document_object import DocumentObject
import pydantic
import datetime as datetime_module


class Types:
    id = types.ImageGroupId
    event_id = types.EventId
    datetime = datetime_module.datetime
    name = types.ImageGroupName
    versions = dict[types.ImageVersionId, version.Version]


class Init:
    id = Types.id
    event_id = Types.event_id
    datetime = Types.datetime | None
    name = Types.name
    versions = Types.versions


class Model(DocumentObject[Init.id]):
    event_id: Init.event_id
    datetime: Init.datetime = pydantic.Field(default=None)
    name: Init.name
    versions: Init.versions = pydantic.Field(
        default_factory=dict, exclude=True)

    @pydantic.field_validator('name')
    def validate_name(cls, v: str):
        if v.endswith(size.Size.Config._SIZE_BEG_TRIGGER):
            raise ValueError('`name` must not end with "{}"'.format(
                size.Size.Config._SIZE_END_TRIGGER))
        if size.Size.Config._VERSION_DELIM in v:
            raise ValueError('`name` must not contain "{}"'.format(
                size.Size.Config._VERSION_DELIM))
        return v


class Group(Model):

    class Config:
        COLLECTION_NAME = 'image_groups'
        ACCEPTABLE_FILE_ENDINGS = {'jpg', 'jpeg', 'png', 'gif', 'cr2',
                                   'bmp', 'tiff', 'tif', 'ico', 'svg', 'webp', 'raw', 'heif', 'heic'}

    def add_image_size(self, im: size.Size):
        if im.version not in self.versions:
            self.add_version(version.Version(id=im.version))
        self.versions[im.version].add_image_size(im)

    def add_version(self, version: version.Version):
        self.versions[version.id] = version
