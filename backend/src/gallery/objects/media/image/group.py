from gallery import types
from gallery.objects.bases.document_object import DocumentObject
from gallery.objects.media.image import version, file
import pydantic
import datetime as datetime_module
import typing


class Base:
    pass


class Group(Base, DocumentObject[types.ImageGroupId]):

    event_id: types.EventId
    datetime: datetime_module.datetime | None = pydantic.Field(default=None)
    name: str
    versions: dict[types.VersionId, version.Version] = pydantic.Field(
        default_factory=dict)

    COLLECTION_NAME: typing.ClassVar[str] = 'image_groups'

    @pydantic.field_validator('name')
    def validate_name(cls, v: str):
        if v.endswith(file.File._SIZE_BEG_TRIGGER):
            raise ValueError('`name` must not end with "{}"'.format(
                file.File._SIZE_END_TRIGGER))
        if file.File._VERSION_DELIM in v:
            raise ValueError('`name` must not contain "{}"'.format(
                file.File._VERSION_DELIM))
        return v
