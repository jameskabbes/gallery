import typing
from gallery.objects.db import collection_object
from gallery.objects import media as media_module
from gallery import types


class Medias(collection_object.CollectionObject[types.MediaId, media_module.Media]):
    COLLECTION_NAME: typing.ClassVar[str] = 'medias'
    CHILD_DOCUMENT_CLASS: typing.ClassVar = media_module.Media
