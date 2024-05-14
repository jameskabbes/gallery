from gallery import config, types
from gallery.objects.db import document_object
import typing
import pathlib
from pymongo import collection as pymongo_collection
from gallery.objects import media_types


class Media(document_object.DocumentObject[types.MediaId, str]):
    COLLECTION_NAME: typing.ClassVar[str] = 'media'

    @classmethod
    def find_media_ids_with_stale_event_ids(cls, collection: pymongo_collection.Collection, event_ids: list[types.EventId]) -> set:
        return cls.find_ids(collection, filter={'event_id': {'$nin': [event_ids]}})

    @classmethod
    def find_to_add_and_delete(cls, collection: pymongo_collection.Collection, dir: pathlib.Path, event_id: types.EventId):

        local_id_keys: set[tuple] = set()
        for file in dir.iterdir():
            if file.is_file():

                file_ending = file.suffix[1:]
                file_type = media_types.get_file_type_by_file_ending(
                    file_ending)
                if file_type is None:
                    continue

                file_class_type = media_types.FILE_CLASS_MAPPING[file_type]
                d = file_class_type.parse_filename(file.name)

                print(d)

                d['event_id'] = event_id
                d['media_type'] = file_class_type.media_type

                local_id_keys.add(tuple(d[id_key]
                                  for id_key in file_class_type.IDENTIFYING_KEYS))

        print(local_id_keys)

        return set(), []
