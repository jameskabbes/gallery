from gallery import types
from gallery.objects.media.video import file as video_file
from gallery.objects.media.image import group as image_group

import typing

TYPES_TYPE = typing.Literal['image', 'video']

MediaId = types.ImageGroupId | types.VideoId

TYPE_MAPPING = {
    'image': image_group.Group,
    'video': video_file.File
}
