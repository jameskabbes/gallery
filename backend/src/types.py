import pydantic
import typing

Nanoid = typing.NewType('Nanoid', str)


ORIGINAL_KEY = typing.Literal['_original']
ImageVersion = typing.NewType(
    'ImageVersion', typing.Literal[ORIGINAL_KEY,
                                   ] | str)
ImageSize = typing.NewType('ImageSize', typing.Literal[ORIGINAL_KEY] | str)


AlbumId = typing.NewType('AlbumId', Nanoid)
ImageGroupId = typing.NewType('ImageGroupId', str)
EventId = typing.NewType('EventId', Nanoid)
GalleryId = typing.NewType('GalleryId', Nanoid)
StudioId = typing.NewType('StudioId', Nanoid)


class ImageFile(pydantic.BaseModel):
    version: str
    size: str
    height: int
    width: int
    bytes: int


class ImageVersion(pydantic.BaseModel):
    pass


class ImageGroup(pydantic.BaseModel):
    pass


class Album:
    pass

# a collection of albums


class Event:
    id: EventId
    pass

# a collection of events / albums


class Gallery:
    id: GalleryId


# a collection of galleries
class Studio:
    id: StudioId
