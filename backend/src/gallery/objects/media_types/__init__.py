from gallery import types
from gallery.objects.media_types.bases import file as base_file
from gallery.objects.media_types.video import file as video_file
from gallery.objects.media_types.image import file as image_file

import typing

MEDIA_TYPE = typing.Literal['image.file', 'image.group', 'video.file']
KEYS_TYPE = typing.Literal['image', 'video']

FILE_MAPPING: dict[KEYS_TYPE, base_file.File] = {
    'image': image_file.File,
    'video': video_file.File
}


def get_file_type_by_file_ending(file_ending: types.FileEnding) -> KEYS_TYPE | None:
    """Get media type from given file ending """

    for media_type in FILE_MAPPING:
        if file_ending in FILE_MAPPING[media_type].ACCEPTABLE_FILE_ENDINGS:
            return media_type
    return None
