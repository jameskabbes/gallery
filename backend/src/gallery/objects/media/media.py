import pydantic
from gallery.objects import media
from gallery import types


class Media(pydantic.BaseModel):
    content: dict[media.MediaLoaderId, media.KEYS_TYPE] = pydantic.Field(
        default_factory=dict)

    def load_basic_by_filenames(self, media_type: media.KEYS_TYPE, filenames: list[types.Filename]) -> bool:
        """load basic media instance by filenames"""

        updated = False
        media_loader = media.MEDIA_LOADER_MAPPING[media_type]

        print(media_loader.load_basic_by_filenames(filenames))

        return updated
