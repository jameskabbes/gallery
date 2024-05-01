from typing import TypedDict, Optional, Union
import pydantic
import typing
import datetime as datetime_module
import re
from gallery import config

ImageVersionId = str
ImageSizeId = str
EventId = str
ImageGroupId = str
HexColor = str
ImageId = str


class ImageTypes:
    id = ImageId
    group_id = ImageGroupId
    file_ending = str
    version = ImageVersionId
    size = ImageSizeId
    height = int
    width = int
    bytes = int
    average_color = HexColor


class ImageInit:
    id = ImageTypes.id
    group_id = ImageTypes.group_id
    file_ending = ImageTypes.file_ending
    version = ImageTypes.version | None
    size = ImageTypes.size | None
    height = ImageTypes.height | None
    width = ImageTypes.width | None
    bytes = ImageTypes.bytes | None
    average_color = ImageTypes.average_color | None


class Image(pydantic.BaseModel):

    id: ImageInit.id = pydantic.Field(alias='_id')
    group_id: ImageInit.group_id
    file_ending: ImageInit.file_ending

    version: ImageInit.version = pydantic.Field(
        default=config.ORIGINAL_KEY)
    size: ImageInit.size = pydantic.Field(
        default=config.ORIGINAL_KEY)
    height: ImageInit.height = pydantic.Field(default=None)
    width: ImageInit.width = pydantic.Field(default=None)
    bytes: ImageInit.bytes = pydantic.Field(default=None)
    average_color: ImageInit.average_color = pydantic.Field(default=None)

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


class ImageGroup(pydantic.BaseModel):
    id: ImageGroupId = pydantic.Field(alias='_id')
    event_id: EventId
    name: str

    @pydantic.field_validator('name')
    def validate_name(cls, v: str):
        if v.endswith(Image.Config._SIZE_BEG_TRIGGER):
            raise ValueError('`name` must not end with "{}"'.format(
                Image.Config._SIZE_END_TRIGGER))
        if Image.Config._VERSION_DELIM in v:
            raise ValueError('`name` must not contain "{}"'.format(
                Image.Config._VERSION_DELIM))
        return v


EventDateInit = datetime_module.date | None

# Event


class EventTypes:
    id = EventId
    date = EventDateInit
    name = str


class EventInit:
    id = EventTypes.id
    date = EventTypes.date
    name = EventTypes.name


class Event(pydantic.BaseModel):
    id: EventInit.id = pydantic.Field(alias='_id')
    date: EventInit.date = pydantic.Field(
        default=None, exclude=True)
    name: EventInit.name = pydantic.Field(default=None, exclude=True)

    image_groups: dict[ImageGroupId, ImageGroup] = pydantic.Field(
        default_factory=dict, exclude=True)

    class Config:
        _MEDIA_KEY: str = 'media'
        _DIRECTORY_NAME_DELIM: str = ' '
