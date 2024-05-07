import typing
from gallery.objects.db import collection_object
from gallery.objects import event as event_module
from gallery import types


class Events(collection_object.CollectionObject[types.EventId, event_module.Event]):
    COLLECTION_NAME: typing.ClassVar[str] = 'events'
    CHILD_DOCUMENT_CLASS: typing.ClassVar = event_module.Event
    PluralByIdType: typing.ClassVar = dict[types.EventId, event_module.Event]
