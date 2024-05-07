import pydantic
from gallery import config, types
from gallery.objects.db import document_object


class Media(document_object.DocumentObject[types.MediaId]):
    pass
