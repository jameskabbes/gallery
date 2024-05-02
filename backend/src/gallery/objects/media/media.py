import pydantic
from gallery.objects import media


class Types:
    content = dict[media.MediaId, media.KEYS_TYPE]


class Init:
    content = Types.content


class Model(pydantic.BaseModel):
    content: Init.content = pydantic.Field(default_factory=dict)


class Media(Model):

    def load_content_object(self, id: media.MediaId):

        media_type = self.content[id]

        return self.content[id]

    pass
