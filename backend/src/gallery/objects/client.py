import typing
import pathlib
from gallery import config, utils
from pymongo import database, MongoClient
from gallery.objects import studios, studio, events, event
import nanoid

type uvicorn_port_type = int


class UvicornConfig(typing.TypedDict):
    port: uvicorn_port_type


type mongodb_port_type = int


class MongoDBConfig(typing.TypedDict):
    port: mongodb_port_type
    full_path: pathlib.Path
    folder_name: str
    db: database.Database
    db_name: str
    client: MongoClient


class StudiosConfig(typing.TypedDict):
    full_path: pathlib.Path
    folder_name: str


class ImportConfig(typing.TypedDict):
    full_path: pathlib.Path
    folder_name: str


class Config(typing.TypedDict):
    uvicorn: UvicornConfig
    mongodb: MongoDBConfig
    studios: StudiosConfig
    media_import: ImportConfig
    full_path: pathlib.Path


DefaultConfig: Config = {
    'uvicorn': {
        'port': 8087,
    },
    'mongodb': {
        'port': 27017,
        'folder_name': 'db',
        'db_name': 'gallery'
    },
    'studios': {
        'folder_name': 'studios'
    },
    "media_import": {
        'folder_name': 'media_import'
    },
    'full_path': config.DATA_DIR
}


class PathOrFolderConfig(typing.TypedDict):
    full_path: pathlib.Path
    folder_name: str


def get_path_from_config(d: PathOrFolderConfig, base_dir: pathlib.Path) -> pathlib.Path:
    if 'full_path' in d:
        return d['full_path']
    else:
        return base_dir.joinpath(d['folder_name'])


class Client:

    dir: pathlib.Path
    uvicorn_port: uvicorn_port_type
    pymongo_port: mongodb_port_type
    pymongo_client: MongoClient
    pymongo_dir: pathlib.Path
    db: database.Database  # just calling it db for short
    studios_dir: pathlib.Path
    media_import_dir: pathlib.Path

    def __init__(self, config: Config = {}):

        merged_config: Config = utils.deep_merge_dicts(DefaultConfig, config)

        # dir
        self.dir = merged_config['full_path']

        # uvicorn
        self.uvicorn_port = merged_config['uvicorn']['port']

        # pymongo
        self.pymongo_port = merged_config['mongodb']['port']
        self.pymongo_dir = get_path_from_config(
            merged_config['mongodb'], self.dir)

        if 'client' not in merged_config['mongodb']:
            merged_config['mongodb']['client'] = MongoClient(
                port=merged_config['mongodb']['port'])
        self.pymongo_client = merged_config['mongodb']['client']

        if 'db' not in merged_config['mongodb']:
            merged_config['mongodb']['db'] = merged_config['mongodb']['client'][merged_config['mongodb']['db_name']]
        self.db = merged_config['mongodb']['db']

        # studios
        self.studios_dir = get_path_from_config(
            merged_config['studios'], self.dir)

        # import
        self.media_import_dir = get_path_from_config(
            merged_config['media_import'], self.dir)

    def sync_with_local(self):
        """sync database with local directory contents"""

        if input('Are you sure you want to sync with local? (y/n) ') != 'y':
            return

        # Studios
        studio_id_keys_to_add, studio_ids_to_delete = studios.Studios.find_to_add_and_delete(
            self.db[studios.Studios.COLLECTION_NAME], self.studios_dir)

        print('Studios to add')
        print(studio_id_keys_to_add)
        print('Studios to delete')
        print(studio_ids_to_delete)
        print()

        for studio_id_keys in studio_id_keys_to_add:
            new_studio = studio.Studio.make_from_id_keys(studio_id_keys)
            new_studio.insert(self.db[studios.Studios.COLLECTION_NAME])

        studios.Studios.delete_by_ids(
            self.db[studios.Studios.COLLECTION_NAME], list(studio_ids_to_delete))

        # Events
        # remove events that reference studios that no longer exist
        valid_studios = tuple(self.db[studios.Studios.COLLECTION_NAME].find(projection={
            'dir_name': 1}))

        stale_event_ids = events.Events.find_event_ids_with_stale_studio_ids(
            self.db[events.Events.COLLECTION_NAME], list(
                item[studio.Studio.ID_KEY] for item in valid_studios)
        )

        events.Events.delete_by_ids(
            self.db[events.Events.COLLECTION_NAME], list(stale_event_ids))

        # loop through existing studios and update events
        for studio_obj in valid_studios:
            studio_id = studio_obj[studio.Studio.ID_KEY]
            studio_dir_name = studio_obj['dir_name']

            studio_dir = self.studios_dir.joinpath(studio_dir_name)

            event_id_keys_to_add, event_ids_to_delete = events.Events.find_to_add_and_delete(
                self.db[events.Events.COLLECTION_NAME], studio_dir, studio_id)

            print(studio_obj)
            print(event_id_keys_to_add)
            print(event_ids_to_delete)

            for event_id_keys in event_id_keys_to_add:
                new_event = event.Event.make_from_id_keys(event_id_keys)
                new_event.insert(self.db[events.Events.COLLECTION_NAME])

            events.Events.delete_by_ids(
                self.db[events.Events.COLLECTION_NAME], list(event_ids_to_delete))
