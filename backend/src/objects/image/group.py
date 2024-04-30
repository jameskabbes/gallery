from src import types
import pydantic
import collections.abc
from jameskabbes.gallery.backend.src.objects.image import version


class ImageGroup(pydantic.BaseModel):
    id: types.ImageGroupId
    _versions: dict[types.ImageVersionId, version.ImageVersion]

    class Config:
        _VERSIONS_KEY: str = 'versions'

    @ classmethod
    def get_image_version_ids(cls, image_group_dict: dict) -> collections.abc.KeysView[types.ImageVersionId]:
        return image_group_dict[cls.Config._VERSIONS_KEY].keys()
