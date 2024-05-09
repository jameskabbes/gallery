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


type nanoid_alphabet_type = str
type nanoid_size_type = int


class NanoidConfig(typing.TypedDict):
    alphabet: nanoid_alphabet_type
    size: nanoid_size_type


class ImportConfig(typing.TypedDict):
    full_path: pathlib.Path
    folder_name: str


class Config(typing.TypedDict):
    uvicorn: UvicornConfig
    mongodb: MongoDBConfig
    studios: StudiosConfig
    nanoid: NanoidConfig
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
    'nanoid': {
        'alphabet': '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
        'size': 12
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
    nanoid_alphabet: nanoid_alphabet_type
    nanoid_size: nanoid_size_type
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

        # nanoid
        self.nanoid_alphabet = merged_config['nanoid']['alphabet']
        self.nanoid_size = merged_config['nanoid']['size']

        # import
        self.media_import_dir = get_path_from_config(
            merged_config['media_import'], self.dir)

    def generate_nanoid(self) -> str:
        return nanoid.generate(self.nanoid_alphabet, self.nanoid_size)

    def sync_with_local(self):
        """sync database with local directory contents"""

        if input('Are you sure you want to sync with local? (y/n) ') != 'y':
            return

        # Studios
        # get the local names of the studios to add to the database
        studios.Studios.sync_db_with_local(
            self.db[studios.Studios.COLLECTION_NAME], self.studios_dir, self.nanoid_alphabet, self.nanoid_size)

        # Events
        # remove events that reference studios that no longer exist
        studio_ids = studios.Studios.get_ids(
            self.db[studios.Studios.COLLECTION_NAME])

        # find events where the studio_id is not in the studio_ids
        stale_event_ids = events.Events.get_ids(
            self.db[events.Events.COLLECTION_NAME], {'studio_id': {'$nin': list(studio_ids)}})

        for event_id in stale_event_ids:
            event.Event.delete_by_id(
                self.db[events.Events.COLLECTION_NAME], event_id)

        """
        # sync the events in each studio
        for studio_id in studios_by_id:

            studio_dir = self.studios_dir.joinpath(
                studios_by_id[studio_id].dir_name)

            local_event_datetimes_and_names = set()
            for subdir in studio_dir.iterdir():
                if subdir.is_dir():
                    a = event.Event.parse_directory_name(
                        subdir.name)

                    event_tuple = (a['datetime'], a['name'])
                    if event_tuple in local_event_datetimes_and_names:
                        raise ValueError(
                            'Duplicate event datetime and name found')

                    local_event_datetimes_and_names.add(event_tuple)

            db_events_datetime_and_names = set([(item['datetime'], item['name']) for item in self.db[events.Events.COLLECTION_NAME].find(
                {'studio_id': studio_id}, {'datetime': 1, 'name': 1})])

            db_events_to_add = local_event_datetimes_and_names - db_events_datetime_and_names
            db_events_to_delete = db_events_datetime_and_names - local_event_datetimes_and_names

            print(studios_by_id[studio_id])

            print('Events to Add')
            print(db_events_to_add)

            for event_datetime_and_time in db_events_to_add:
                new_event = event.Event(
                    _id=event.Event.generate_id(self.nanoid_alphabet, self.nanoid_size), studio_id=studio_id, datetime=event_datetime_and_time[0], name=event_datetime_and_time[1])
                print(new_event)
                new_event.insert(self.db[events.Events.COLLECTION_NAME])

            print('Events to delete')
            print(db_events_to_delete)

            for event_datetime_and_time in db_events_to_delete:
                event.Event.delete_by_datetime_and_name(
                    self.db[events.Events.COLLECTION_NAME], studio_id, event_datetime_and_time[0], event_datetime_and_time[1])
        """
