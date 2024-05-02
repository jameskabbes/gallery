from gallery import types, config
import pydantic
import re


class Types:
    id = types.ImageId
    group_id = types.ImageGroupId
    file_ending = str
    version = types.ImageVersionId
    size = types.ImageSizeId
    height = int
    width = int
    bytes = int
    average_color = types.HexColor


class Init:
    id = Types.id
    group_id = Types.group_id
    file_ending = Types.file_ending
    version = Types.version | None
    size = Types.size | None
    height = Types.height | None
    width = Types.width | None
    bytes = Types.bytes | None
    average_color = Types.average_color | None


class Model(pydantic.BaseModel):

    id: Init.id = pydantic.Field(alias='_id')
    group_id: Init.group_id
    file_ending: Init.file_ending

    version: Init.version = pydantic.Field(
        default=config.ORIGINAL_KEY)
    size: Init.size = pydantic.Field(
        default=config.ORIGINAL_KEY)
    height: Init.height = pydantic.Field(default=None)
    width: Init.width = pydantic.Field(default=None)
    bytes: Init.bytes = pydantic.Field(default=None)
    average_color: Init.average_color = pydantic.Field(default=None)

    class Config:
        _VERSION_DELIM = '-'
        _SIZE_BEG_TRIGGER = '('
        _SIZE_END_TRIGGER = ')'

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

    @ pydantic.field_validator('height', 'width', 'bytes')
    def validate_positive(cls, v):
        if v is not None and v < 0:
            raise ValueError('must be None or greater than or equal to 0')
        return v

    @ pydantic.field_validator('average_color')
    def validate_average_color(cls, v):
        if v is not None and not re.match("^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$", v):
            raise ValueError('average_color must be a valid hex color or None')
        return v


class Size(Model):
    pass
