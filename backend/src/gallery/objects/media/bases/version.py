from gallery import types
from gallery.objects.media.image import file
import pydantic
import typing


ChildFile = typing.TypeVar('ChildFile', bound=file.File)


class Version(pydantic.BaseModel, typing.Generic[ChildFile]):

    views: int
    downloads: int
    sizes: dict[types.SizeId, ChildFile] = pydantic.Field(
        default_factory=dict)

    def add_child_file(self, file: ChildFile):
        self.sizes[file.id] = file
