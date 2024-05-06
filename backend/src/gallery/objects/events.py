import typing
from gallery.objects.db import collection_object
from gallery.objects import event


class Events(collection_object.CollectionObject):
    COLLECTION_NAME: typing.ClassVar[str] = 'events'
    CHILD_DOCUMENT_CLASS: typing.ClassVar = event.Event
    ChildIdType: typing.ClassVar = event.Event.IdType
