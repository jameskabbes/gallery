import pydantic
from gallery.objects import media


class Types:
    content = dict[media.MediaId, media.TYPES_TYPE]


class Init:
    content = Types.content


class Model(pydantic.BaseModel):
    content = Init.content = pydantic.Field(default_factory=dict)


class Media(Model):
    pass
