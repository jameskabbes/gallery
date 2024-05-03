import pydantic
from gallery import types
from gallery.objects.media.bases import version as base_version, file as base_file
import datetime as datetime_module
import typing


class Group(pydantic.BaseModel):

    event_id: types.EventId
    datetime: datetime_module.datetime | None = pydantic.Field(default=None)
    name: str
    versions: dict[types.VersionId, ChildVersion] = pydantic.Field(
        default_factory=dict)

    def add_version(self, version: ChildVersion):
        self.versions[version.id] = version

    @pydantic.field_validator('name')
    def validate_name(cls, v: str):
        if v.endswith(ChildFile.Config._SIZE_BEG_TRIGGER):
            raise ValueError('`name` must not end with "{}"'.format(
                ChildFile.Config._SIZE_END_TRIGGER))
        if ChildFile.Config._VERSION_DELIM in v:
            raise ValueError('`name` must not contain "{}"'.format(
                ChildFile.Config._VERSION_DELIM))
        return v
