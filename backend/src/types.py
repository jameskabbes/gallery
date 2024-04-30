import pydantic
import typing
import datetime as datetime_module

ORIGINAL_KEY = typing.Literal['_original']

ImageVersionId = typing.Literal[ORIGINAL_KEY] | str
ImageSizeId = typing.Literal[ORIGINAL_KEY] | str
EventId = str
ImageGroupId = str
