from gallery import types
import pydantic
from gallery.objects.image import image, version
from pymongo import collection


class Group(pydantic.BaseModel):
    id: types.ImageGroupId
    versions: dict[types.ImageVersionId,
                   version.Version] = pydantic.Field(default_factory=dict, exclude=True)

    class Config:
        _VERSIONS_KEY: str = 'versions'

    def add_image(self, im: image.Image):
        if im.version_id not in self.versions:
            self.add_version(version.Version(id=im.version_id))
        self.versions[im.version_id].add_image(im)

    def add_version(self, version: version.Version):
        self.versions[version.id] = version
