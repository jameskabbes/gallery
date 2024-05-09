import typing
from gallery.objects.db import collection_object
from gallery.objects import event as event_module
from gallery import types, config
from pymongo import collection
import pathlib


class Events(collection_object.CollectionObject[types.EventId, event_module.Event]):
    COLLECTION_NAME: typing.ClassVar[str] = 'events'
    CHILD_DOCUMENT_CLASS: typing.ClassVar = event_module.Event
    PluralByIdType: typing.ClassVar = dict[types.EventId, event_module.Event]

    @classmethod
    def find_child_document_id_keys_in_dir(cls, dir: pathlib.Path) -> set[tuple]:
        local_ids_keys = set()
        for subdir in dir.iterdir():
            if subdir.is_dir():
                local_ids_keys.add(
                    cls.CHILD_DOCUMENT_CLASS.parse_into_id_keys(subdir.name))
        return local_ids_keys
