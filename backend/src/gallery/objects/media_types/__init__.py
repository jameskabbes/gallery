from gallery import types
from gallery.objects.media_types.video import file as video_file
from gallery.objects.media_types.image import file as image_file
from gallery.objects.media_types.image import group as image_group
import typing

FileClassMappingType = typing.TypedDict('FileClassMappingType', {
    'image': image_file.File,
    'video': video_file.File
})

FILE_CLASS_MAPPING: FileClassMappingType = {
    'image': image_file.File,
    'video': video_file.File
}

FileLoaderMappingType = typing.TypedDict('FileLoaderMappingType', {
    'image': image_group.Group,
    'video': video_file.File
})

FILE_LOADER_MAPPING: dict[types.MediaCoreType] = {
    'image': image_group.Group,
    'video': video_file.File
}


def get_file_type_by_file_ending(file_ending: types.FileEnding) -> types.MediaCoreType | None:
    """Get media type from given file ending """

    for media_type in FILE_CLASS_MAPPING:
        if file_ending in FILE_CLASS_MAPPING[media_type].ACCEPTABLE_FILE_ENDINGS:
            return media_type
    return None
