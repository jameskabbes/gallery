import pydantic
import typing
import datetime as datetime_module

ORIGINAL_KEY = typing.Literal['_original']

ImageVersionId = typing.Literal[ORIGINAL_KEY] | str
ImageSizeId = typing.Literal[ORIGINAL_KEY] | str
EventId = str
ImageGroupId = str
ImageId = str


class Image(pydantic.BaseModel):
    id: ImageId = pydantic.Field(init=False)
    group_id: ImageGroupId
    version_id: ImageVersionId | None = pydantic.Field(
        default=None)
    size_id: ImageSizeId | None = pydantic.Field(
        default=None)
    extension: str
