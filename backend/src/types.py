import pydantic
import typing
import datetime as datetime_module

Nanoid = typing.NewType('Nanoid', str)


ORIGINAL_KEY = typing.Literal['_original']

ImageVersion = typing.Literal[ORIGINAL_KEY] | str
ImageSize = typing.Literal[ORIGINAL_KEY] | str
EventId = str


class ImageFile(pydantic.BaseModel):
    image_version: ImageVersion | None
    size: ImageSize | None
    height: int
    width: int
    bytes: int


class Album:
    pass


class ImageGroupId(str):
    pass


class Event(pydantic.BaseModel):
    id: EventId
