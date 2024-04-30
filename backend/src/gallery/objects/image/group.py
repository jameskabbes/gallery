from gallery import types
import pydantic
from gallery.objects.image import version, file
from pymongo import collection


class Group(pydantic.BaseModel):
    id: types.ImageGroupId
    versions: dict[types.ImageVersionId,
                   version.Version] = pydantic.Field(default_factory=dict, exclude=True)

    class Config:
        _VERSIONS_KEY: str = 'versions'

    def add_file(self, file: file.File):
        if file.version_id not in self.versions:
            self.add_version(version.Version(id=file.version_id))
        self.versions[file.version_id].add_file(file)

    def add_version(self, version: version.Version):
        self.versions[version.id] = version
