from gallery import types
from gallery.objects.db import document_object
from gallery.objects.media_types.image import version, file
from gallery.objects.media_types.bases import content_loader
import pydantic
import datetime as datetime_module
from pymongo import collection
import typing


class Base:
    Basics = dict[types.ImageGroupName,
                  dict[types.VersionId, dict[types.SizeId, set[types.FileEnding]]]]


class Group(Base, document_object.DocumentObject[types.ImageGroupId], content_loader.ContentLoader):

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

    def add_file(self, image_file: file.File):
        """Add file id to group"""

        if image_file.version not in self.versions:
            self.versions[image_file.version] = version.Version()

        self.versions[image_file.version].add_file(image_file)

    @classmethod
    def load_basic_by_filenames(cls, filenames: list[types.Filename]) -> Base.Basics:

        group_basics_by_name: Base.Basics = {}

        for filename in filenames:
            image_filename_io_dict = file.File.parse_filename(filename)

            image_group_name = image_filename_io_dict['group_name']
            image_file_ending = image_filename_io_dict['file_ending']
            image_size = image_filename_io_dict['size']
            image_version = image_filename_io_dict['version']

            # check image group name
            if image_group_name not in group_basics_by_name:
                group_basics_by_name[image_group_name] = {}

            # check image version
            if image_version not in group_basics_by_name[image_group_name]:
                group_basics_by_name[image_group_name][image_version] = {}

            # check image size
            if image_size not in group_basics_by_name[image_group_name][image_version]:
                group_basics_by_name[image_group_name][image_version][image_size] = set(
                )

            # add file ending
            group_basics_by_name[image_group_name][image_version][image_size].add(
                image_file_ending)

        return group_basics_by_name
