import typing
import pathlib
from gallery import config, utils
from pymongo import database, MongoClient


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
        print(merged_config)

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
