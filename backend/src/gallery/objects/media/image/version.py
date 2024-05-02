from gallery import types
from gallery.objects.media.image import file
import pydantic


class Types:
    views = int
    downloads = int
    sizes = dict[types.ImageSizeId, file.File]
    pass


class Init:
    views = Types.views
    downloads = Types.downloads
    sizes = Types.sizes


class Model(pydantic.BaseModel):
    views: Init.views
    downloads: Init.downloads
    sizes: dict[types.ImageSizeId, file.File] = pydantic.Field(
        default_factory=dict, exclude=True)


class Version(Model):
    def add_image_size(self, size: file.File):
        self.sizes[size.id] = size
