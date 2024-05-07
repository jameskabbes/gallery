import typing
from gallery.objects.db import collection_object
from gallery.objects import event as event_module
from gallery import types


class Events(collection_object.CollectionObject[event_module.Event, types.EventId]):
    COLLECTION_NAME: typing.ClassVar[str] = 'events'
    CHILD_DOCUMENT_CLASS: typing.ClassVar = event_module.Event
