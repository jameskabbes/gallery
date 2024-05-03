from gallery import types, config
import pydantic
import typing


class Init:
    version = types.VersionId
    size = types.SizeId
    file_ending = types.FileEnding


class File(pydantic.BaseModel):

    group_id: types.GroupId
    file_ending: Init.file_ending
    version: Init.version = pydantic.Field(default=config.ORIGINAL_KEY)
    size: Init.size = pydantic.Field(default=config.ORIGINAL_KEY)

    ACCEPTABLE_FILE_ENDINGS: set[types.FileEnding] = set()

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

    @pydantic.field_validator('version')
    def validate_version(cls, v):
        if v is not None and cls.Config._VERSION_DELIM in v:
            raise ValueError('`version` must not contain "{}"'.format(
                cls.Config._VERSION_DELIM))
        return v

    @ pydantic.field_validator('size')
    def validate_size(cls, v):
        if v is not None and (cls.Config._SIZE_BEG_TRIGGER in v or cls.Config._SIZE_END_TRIGGER in v):
            raise ValueError('`size` cannot contain "{}" or "{}"'.format(
                cls.Config._SIZE_BEG_TRIGGER, cls.Config._SIZE_END_TRIGGER))
        return v
