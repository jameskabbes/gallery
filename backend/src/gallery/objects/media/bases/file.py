from gallery import types, config
import pydantic
import typing


GroupIdType = typing.TypeVar(
    'GroupIdType', bound=types.ImageGroupId | types.VideoId)


class Init:
    version = types.VersionId
    size = types.SizeId
    file_ending = types.FileEnding


class File(pydantic.BaseModel, typing.Generic[GroupIdType]):

    event_id: types.EventId
    group_id: GroupIdType
    file_ending: Init.file_ending
    version: Init.version = pydantic.Field(default=config.ORIGINAL_KEY)
    size: Init.size = pydantic.Field(default=config.ORIGINAL_KEY)

    class Config:
        _VERSION_DELIM = '-'
        _SIZE_BEG_TRIGGER = '('
        _SIZE_END_TRIGGER = ')'
        _FILENAME_TYPE = str

        class FilenameIODict(typing.TypedDict):
            group_name: types.ImageGroupName
            version: Init.version
            size: Init.size
            file_ending: Init.file_ending
