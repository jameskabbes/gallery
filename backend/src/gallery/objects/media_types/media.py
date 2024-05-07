import pydantic
from gallery.objects import media_types
from gallery import types


class Media(pydantic.BaseModel):
    content: dict[media_types.MediaLoaderId, media_types.KEYS_TYPE] = pydantic.Field(
        default_factory=dict)

    def load_basic_by_filenames(self, media_type: media_types.KEYS_TYPE, filenames: list[types.Filename]) -> bool:
        """load basic media instance by filenames"""

        updated = False
        media_loader = media_types.MEDIA_LOADER_MAPPING[media_type]

        print(media_loader.load_basic_by_filenames(filenames))

        return updated
