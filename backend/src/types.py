import pydantic
import typing

Nanoid = typing.NewType('Nanoid', str)

ImageFileId = typing.NewType('ImageFileId', Nanoid)
ImageVersionId = typing.NewType('ImageVersionId', Nanoid)
ImageGroupId = typing.NewType('ImageGroupId', Nanoid)
AlbumId = typing.NewType('AlbumId', Nanoid)
EventId = typing.NewType('EventId', Nanoid)
GalleryId = typing.NewType('GalleryId', Nanoid)
StudioId = typing.NewType('StudioId', Nanoid)


class ImageFile(pydantic.BaseModel):
    id: ImageFileId
    shape: tuple[int, int]
    size: int


class ImageVersion(pydantic.BaseModel):
    id: ImageVersionId
    group_id: ImageGroupId


class ImageGroup(pydantic.BaseModel):
    id: ImageGroupId


class Album:
    pass

# a collection of albums


class Event:
    pass

# a collection of events / albums


class Gallery:
    pass


# a collection of galleries
class Studio:
    pass
