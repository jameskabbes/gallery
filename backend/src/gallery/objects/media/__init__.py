from gallery import types
from gallery.objects.media.video import file as video_file
from gallery.objects.media.image import file as image_file

import typing

KEYS_TYPE = typing.Literal['image', 'video']
OBJECTS_TYPE = image_file.File | video_file.File

MediaId = types.ImageGroupId | types.VideoId

TYPE_MAPPING: dict[KEYS_TYPE, OBJECTS_TYPE] = {
    'image': image_file.File,
    'video': video_file.File
}


def get_media_type(file_ending: types.FileEnding) -> KEYS_TYPE | None:
    """Get media type from given file ending """

    for media_type in TYPE_MAPPING:
        if file_ending in TYPE_MAPPING[media_type].Config.ACCEPTABLE_FILE_ENDINGS:
            return media_type
    return None
