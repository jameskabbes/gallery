from gallery import types
from gallery.objects.image import image
import pydantic
import collections.abc


class Version(pydantic.BaseModel):
    id: types.ImageVersionId
    sizes: dict[types.ImageSizeId, image.Image] = pydantic.Field(
        default_factory=dict, exclude=True)

    class Config:
        _SIZES_KEY: str = 'sizes'

    @pydantic.root_validator(pre=True)
    def check_original_version(cls, values):

        if values['id'] == None:
            values['id'] = types.ORIGINAL_KEY
        return values

    @classmethod
    def get_image_file_sizes(cls, image_version_dict: dict) -> collections.abc.KeysView[types.ImageSizeId]:
        return image_version_dict[cls.Config._SIZES_KEY].keys()

    def add_image(self, file: image.Image):
        self.sizes[file.size_id] = file
