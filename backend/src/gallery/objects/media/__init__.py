from gallery import types
from gallery.objects.media.video import file as video_file
from gallery.objects.media.image import group as image_group

import typing

KEYS_TYPE = typing.Literal['image', 'video']
OBJECTS_TYPE = image_group.Group | video_file.File

MediaId = types.ImageGroupId | types.VideoId

TYPE_MAPPING: dict[KEYS_TYPE, OBJECTS_TYPE] = {
    'image': image_group.Group,
    'video': video_file.File
}
