from src import types
import pydantic
import collections.abc


class ImageVersion(pydantic.BaseModel):
    id: types.ImageVersionId

    _SIZES_KEY: str = 'sizes'

    @classmethod
    def get_image_file_sizes(cls, image_version_dict: dict) -> collections.abc.KeysView[types.ImageSizeId]:
        print(image_version_dict)
        return image_version_dict[cls._SIZES_KEY].keys()


class ImageVersions:
    pass
