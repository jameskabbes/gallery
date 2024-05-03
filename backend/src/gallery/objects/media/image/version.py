import pydantic
from gallery import types
from gallery.objects.media.image import file


class Version(pydantic.BaseModel):

    views: int = pydantic.Field(default=0)
    downloads: int = pydantic.Field(default=0)
    sizes: dict[types.SizeId, file.File] = pydantic.Field(default_factory=dict)
