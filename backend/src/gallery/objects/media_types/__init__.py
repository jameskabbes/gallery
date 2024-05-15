from gallery import types

from gallery.objects.media_types import image as image_module, video as video_module, audio as audio_module

from gallery.objects.media_types.video import file as video_file
from gallery.objects.media_types.image import file as image_file
from gallery.objects.media_types.audio import file as audio_file

import typing

MEDIA_CORE_TYPES = ('image', 'video', 'audio')
FileClassTypes = image_file.File | video_file.File | audio_file.File

ModuleMappingType = typing.TypedDict('ModuleMappingType', {
    'image': image_module,
    'video': video_module,
    'audio': audio_module
})

MODULE_MAPPING: ModuleMappingType = {
    'image': image_module,
    'video': video_module,
    'audio': audio_module
}


FileClassMappingType = typing.TypedDict('FileClassMappingType', {
    'image': image_file.File,
    'video': video_file.File,
    'audio': audio_file.File
})

FILE_CLASS_MAPPING: FileClassMappingType = {
    'image': image_file.File,
    'video': video_file.File,
    'audio': audio_file.File
}


def get_media_core_type_from_file_ending(file_ending: types.FileEnding) -> types.MediaCoreType | None:
    """Get media type from given file ending """

    for media_type in FILE_CLASS_MAPPING:
        if file_ending in FILE_CLASS_MAPPING[media_type].ACCEPTABLE_FILE_ENDINGS:
            return media_type
    return None
