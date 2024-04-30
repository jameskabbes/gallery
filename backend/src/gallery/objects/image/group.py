from src import types
import pydantic
from src.objects.image import version
from pymongo import collection


class ImageGroup(pydantic.BaseModel):
    id: types.ImageGroupId
    _versions: dict[types.ImageVersionId, version.ImageVersion]

    class Config:
        _VERSIONS_KEY: str = 'versions'


class ImageGroups:

    @staticmethod
    def get_image_groups_ids(collection_event: collection.Collection) -> set[types.ImageGroupId]:
        """Returns a set of image groups ids."""
        return set([item['_id'] for item in collection_event.find({}, {'_id': 1})])
