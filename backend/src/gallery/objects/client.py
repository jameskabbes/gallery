import typing
import pathlib
from gallery import config, utils
from pymongo import database, MongoClient
from gallery.objects import studio, event, media

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
        studio_id_keys_to_add, studio_ids_to_delete = studio.Studio.find_to_add_and_delete(
            self.db[studio.Studio.COLLECTION_NAME], self.studios_dir)

        print('Studios to add')
        print(studio_id_keys_to_add)
        print('Studios to delete')
        print(studio_ids_to_delete)
        print()

        for studio_id_keys in studio_id_keys_to_add:
            new_studio = studio.Studio.make_from_id_keys(studio_id_keys)
            new_studio.insert(self.db[studio.Studio.COLLECTION_NAME])

        studio.Studio.delete_by_ids(
            self.db[studio.Studio.COLLECTION_NAME], list(studio_ids_to_delete))

        # Events
        # remove events that reference studios that no longer exist
        studio_id_keys_by_id = studio.Studio.find_id_keys_by_id(
            self.db[studio.Studio.COLLECTION_NAME])

        stale_event_ids = event.Event.find_event_ids_with_stale_studio_ids(
            self.db[event.Event.COLLECTION_NAME], list(
                studio_id_keys_by_id.keys())
        )

        print('Stale event ids')
        print(stale_event_ids)
        print()

        event.Event.delete_by_ids(
            self.db[event.Event.COLLECTION_NAME], list(stale_event_ids))

        # loop through existing studios and update events
        for studio_id in studio_id_keys_by_id:
            studio_dir_name = studio_id_keys_by_id[studio_id][0]
            studio_dir = self.studios_dir.joinpath(studio_dir_name)

            event_id_keys_to_add, event_ids_to_delete = event.Event.find_to_add_and_delete(
                self.db[event.Event.COLLECTION_NAME], studio_dir, studio_id)

            print(studio_id)
            print(event_id_keys_to_add)
            print(event_ids_to_delete)
            print()

            for event_id_keys in event_id_keys_to_add:
                new_event = event.Event.make_from_id_keys(event_id_keys)
                new_event.insert(self.db[event.Event.COLLECTION_NAME])

            event.Event.delete_by_ids(
                self.db[event.Event.COLLECTION_NAME], list(event_ids_to_delete))

        # Medias
        # remove medias that reference events that no longer exist
        event_id_keys_by_id = event.Event.find_id_keys_by_id(
            self.db[event.Event.COLLECTION_NAME])

        stale_media_ids = media.Media.find_media_ids_with_stale_event_ids(
            self.db[media.Media.COLLECTION_NAME], list(
                event_id_keys_by_id.keys())
        )

        print('Stale media ids')
        print(stale_media_ids)
        print()

        media.Media.delete_by_ids(
            self.db[media.Media.COLLECTION_NAME], list(stale_media_ids))

        for event_id in event_id_keys_by_id:
            event_datetime = event_id_keys_by_id[event_id][0]
            event_name = event_id_keys_by_id[event_id][1]
            event_studio_id = event_id_keys_by_id[event_id][2]

            event_dir = self.studios_dir.joinpath(studio_id_keys_by_id[event_studio_id][0]).joinpath(
                event.Event.build_directory_name(
                    {'datetime': event_datetime, 'name': event_name})
            )

            media_id_keys_to_add, media_ids_to_delete = media.Media.find_to_add_and_delete(
                self.db[event.Event.COLLECTION_NAME], event_dir, event_id)
