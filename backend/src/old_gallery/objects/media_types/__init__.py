from gallery import custom_types

from gallery.objects.media_types import image, video, audio


import typing

TYPES = ('image', 'video', 'audio')
FILE_CLASS_TYPE = image.File | video.File | audio.File

ModuleMappingType = typing.TypedDict('ModuleMappingType', {
    'image': image,
    'video': video,
    'audio': audio
})

MODULE_MAPPING: ModuleMappingType = {
    'image': image,
    'video': video,
    'audio': audio
}


FileClassMappingType = typing.TypedDict('FileClassMappingType', {
    'image': image.File,
    'video': video.File,
    'audio': audio.File
})

FILE_CLASS_MAPPING: FileClassMappingType = {
    'image': image.File,
    'video': video.File,
    'audio': audio.File
}


def get_media_type_from_file_ending(file_ending: custom_types.FileEnding) -> custom_types.MediaType | None:
    """Get media type from given file ending """

    for media_type in TYPES:
        if file_ending in FILE_CLASS_MAPPING[media_type].ACCEPTABLE_FILE_ENDINGS:
            return media_type
    return None
