import pydantic
import typing

Nanoid = typing.NewType('Nanoid', str)


ORIGINAL_KEY = typing.Literal['_original']


class ImageVersion(pydantic.BaseModel):
    version: typing.Literal[ORIGINAL_KEY] | str


class ImageSize(pydantic.BaseModel):
    size: typing.Literal[ORIGINAL_KEY] | str


class ImageGroupId(str):
    pass


class ImageGroup(pydantic.BaseModel):
    pass


class ImageVersion(pydantic.BaseModel):
    pass


class ImageFile(pydantic.BaseModel):
    image_version: ImageVersion | None
    size: typing.Optional[ImageSize]
    height: int
    width: int
    bytes: int


class Album:
    pass
