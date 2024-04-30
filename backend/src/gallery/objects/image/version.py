from gallery import types
from gallery.objects.image import file
import pydantic
import collections.abc


class Version(pydantic.BaseModel):
    id: types.ImageVersionId
    sizes: dict[types.ImageSizeId, file.File] = pydantic.Field(
        default_factory=dict, exclude=True)

    class Config:
        _SIZES_KEY: str = 'sizes'

    @classmethod
    def get_image_file_sizes(cls, image_version_dict: dict) -> collections.abc.KeysView[types.ImageSizeId]:
        print(image_version_dict)
        return image_version_dict[cls.Config._SIZES_KEY].keys()

    def add_file(self, file: file.File):
        self.sizes[file.size_id] = file
