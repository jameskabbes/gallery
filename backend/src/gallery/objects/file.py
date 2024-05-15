from pymongo import database, collection as pymongo_collection, MongoClient
from gallery import types
from gallery.objects.bases import document_object, collection_object
from gallery.objects import file_types
import pydantic
import datetime as datetime_module
import pathlib
import typing


class File(collection_object.CollectionObject[types.FileId]):
    COLLECTION_NAME: typing.ClassVar[str] = 'files'
    MEDIA_TYPE_ID_KEY_INDEX: typing.ClassVar[int] = 0

    @ classmethod
    def find_to_add_and_delete(cls, collection: pymongo_collection.Collection, dir: pathlib.Path, event_id: types.EventId) -> tuple[set[tuple], set[types.MediaId]]:

        local_id_keys_by_media_type: dict[file_types.MEDIA_CORE_TYPES, set[tuple]] = {
        }

        for media_core_type in file_types.MEDIA_CORE_TYPES:
            local_id_keys_by_media_type[media_core_type] = set()

        for file in dir.iterdir():
            if file.is_file():

                file_ending = file.suffix[1:]
                media_core_type = file_types.get_media_core_type_from_file_ending(
                    file_ending)

                if media_core_type is None:
                    Warning('File ending not recognized {} not recognized on file {}'.format(
                        file_ending, file))
                    continue

                if media_core_type not in local_id_keys_by_media_type:
                    local_id_keys_by_media_type[media_core_type] = set()

                file_class = file_types.FILE_CLASS_MAPPING[media_core_type]
                dict_id_keys = file_class.parse_filename(file.name)
                dict_id_keys['event_id'] = event_id
                dict_id_keys['media_type'] = media_core_type
                dict_id_keys['relative_path'] = str(
                    file.parent.relative_to(dir))

                print(dict_id_keys)

                id_keys_tuple = file_class.dict_id_keys_to_tuple(dict_id_keys)
                if id_keys_tuple in local_id_keys_by_media_type[media_core_type]:
                    raise ValueError(
                        'Duplicate file found in directory {}'.format(file))

                local_id_keys_by_media_type[media_core_type].add(id_keys_tuple)

        # ids and id_keys in the database
        id_keys_to_add = set()
        ids_to_remove = set()

        for media_core_type in file_types.MEDIA_CORE_TYPES:
            file_class = file_types.FILE_CLASS_MAPPING[media_core_type]

            db_id_by_id_keys = file_class.find_id_by_id_keys(
                collection, {'event_id': event_id, 'media_type': media_core_type})

            db_id_keys = set(db_id_by_id_keys.keys())

            id_keys_to_add.update(
                local_id_keys_by_media_type[media_core_type] - db_id_keys)
            ids_to_remove.update(
                db_id_keys - local_id_keys_by_media_type[media_core_type])

        return id_keys_to_add, ids_to_remove
