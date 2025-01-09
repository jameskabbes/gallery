import typing
import pathlib
from pydantic import EmailStr, StringConstraints
from gallery import utils
from sqlalchemy import create_engine, Engine
from sqlmodel import SQLModel
import datetime
import json
from pathlib import Path
import jwt

GALLERY_DIR = Path(__file__).parent
SRC_DIR = GALLERY_DIR.parent
BACKEND_DIR = SRC_DIR.parent
REPO_DIR = BACKEND_DIR.parent
REPO_DATA_DIR = REPO_DIR / 'data'
PROJECT_CONFIG_PATH = REPO_DIR / 'config.json'

FASTAPI_RUN_PATH = SRC_DIR / 'fastapi_run.sh'
FASTAPI_DEV_PATH = SRC_DIR / 'fastapi_dev.sh'

REQUIREMENTS_INSTALLED_PATH = SRC_DIR / 'requirements_installed.txt'


class PermissionLevelTypes:
    id = int
    name = typing.Literal['editor', 'viewer']


class VisibilityLevelTypes:
    id = int
    name = typing.Literal['public', 'private']


class ScopeTypes:
    id = int
    name = typing.Literal['admin', 'users.read', 'users.write']


class UserRoleTypes:
    id = int
    name = typing.Literal['admin', 'user']


type uvicorn_port_type = int
PhoneNumber = str
Email = typing.Annotated[EmailStr, StringConstraints(
    min_length=1, max_length=254)]


class PathConfig(typing.TypedDict):
    path: pathlib.Path
    parent_dir: pathlib.Path
    filename: str


class UvicornConfig(typing.TypedDict):
    port: uvicorn_port_type


class DbConfig(typing.TypedDict):
    engine: Engine
    path: PathConfig


class MediaRootConfig(typing.TypedDict):
    path: PathConfig


class AuthenticationConfig(typing.TypedDict):
    stay_signed_in_default: bool
    expiry_timedeltas: dict[typing.Literal['default_access_token',
                                           'request_magic_link', 'request_sign_up'], datetime.timedelta]


class JWTConfig(typing.TypedDict):
    secret_key_path: PathConfig
    algorithm: str


class GoogleClientConfig(typing.TypedDict):
    path: PathConfig


class Config(typing.TypedDict):
    uvicorn: UvicornConfig
    db: DbConfig
    media_root: MediaRootConfig
    authentication: AuthenticationConfig
    jwt: JWTConfig
    google_client: GoogleClientConfig


DefaultConfig: Config = {
    'uvicorn': {
        'port': 8087,
    },
    'db': {
        'path': {
            'parent_dir': BACKEND_DIR,
            'filename': 'data/gallery.db',
        }
    },
    'media_root': {
        'path': {
            'parent_dir': BACKEND_DIR,
            'filename': 'data/media_root'
        }
    },

    'authentication': {
        'stay_signed_in_default': False,
        'expiry_timedeltas': {
            'default_access_token': datetime.timedelta(days=7),
            'request_magic_link': datetime.timedelta(minutes=10),
            'request_sign_up': datetime.timedelta(hours=1),
        }

    },
    'jwt': {
        'secret_key_path': {
            'parent_dir': BACKEND_DIR,
            'filename': 'data/jwt_secret_key.txt'
        },
        'algorithm': 'HS256'
    },
    'google_client': {
        'path': {
            'parent_dir': REPO_DATA_DIR,
            'filename': 'google_client_secret.json'
        }}
}


def get_path_from_config(d: PathConfig) -> pathlib.Path:
    if 'path' in d:
        return d['path']

    if 'parent_dir' in d:
        if 'filename' in d:
            return d['parent_dir'].joinpath(d['filename'])

        raise ValueError('dir key must be accompanied by filename or folder')
    raise ValueError('path or dir key must be present')


class Client:

    uvicorn_port: uvicorn_port_type
    db_engine: Engine
    media_dir: pathlib.Path
    galleries_dir: pathlib.Path
    authentication: AuthenticationConfig
    jwt_secret_key: str
    jwt_algorithm: str
    root_config: dict
    google_client: dict

    auth_key: str
    header_keys: dict[str, str]
    cookie_keys: dict[str, str]
    frontend_urls: dict[str, str]

    scope_name_mapping: dict[ScopeTypes.name, ScopeTypes.id]
    scope_id_mapping: dict[ScopeTypes.id, ScopeTypes.name]
    visibility_level_name_mapping: dict[VisibilityLevelTypes.name,
                                        VisibilityLevelTypes.id]
    permission_level_name_mapping: dict[PermissionLevelTypes.name,
                                        PermissionLevelTypes.id]
    user_role_name_mapping: dict[UserRoleTypes.name,
                                 UserRoleTypes.id]

    user_role_id_scope_ids: dict[UserRoleTypes.id,
                                 set[ScopeTypes.id]]

    def __init__(self, config: Config = {}):

        merged_config: Config = utils.deep_merge_dicts(DefaultConfig, config)

        # uvicorn
        self.uvicorn_port = merged_config['uvicorn']['port']

        # db
        db_engine_path = get_path_from_config(merged_config['db']['path'])
        self.db_engine = create_engine(f'sqlite:///{db_engine_path}')

        # media dir
        self.media_dir = get_path_from_config(
            merged_config['media_root']['path'])

        if not self.media_dir.exists():
            self.media_dir.mkdir()

        # galleries dir
        self.galleries_dir = self.media_dir / 'galleries'
        if not self.galleries_dir.exists():
            self.galleries_dir.mkdir()

        # authentication
        self.authentication = merged_config['authentication']

        # jwt
        jwt_secret_key_path = get_path_from_config(
            merged_config['jwt']['secret_key_path'])
        self.jwt_secret_key = jwt_secret_key_path.read_text()
        self.jwt_algorithm = merged_config['jwt']['algorithm']

        # google client
        google_client_path = get_path_from_config(
            merged_config['google_client']['path'])
        self.google_client = json.loads(google_client_path.read_text())

        # root config
        self.root_config = json.loads(
            pathlib.Path('../../config.json').read_text())

        # auth_key
        self.auth_key = self.root_config['auth_key']

        # header_keys
        self.header_keys = self.root_config['header_keys']

        # cookie_keys
        self.cookie_keys = self.root_config['cookie_keys']

        # frontend_urls
        self.frontend_urls = self.root_config['frontend_urls']

        # scope_name_mapping
        self.scope_name_mapping = self.root_config['scope_name_mapping']

        self.scope_id_mapping = {}
        for scope_name in self.scope_name_mapping:
            self.scope_id_mapping[self.scope_name_mapping[scope_name]] = scope_name

        # visibility_level_name_mapping
        self.visibility_level_name_mapping = self.root_config['visibility_level_name_mapping']

        # permission_level_name_mapping
        self.permission_level_name_mapping = self.root_config['permission_level_name_mapping']

        # user_role_name_mapping
        self.user_role_name_mapping = self.root_config['user_role_name_mapping']

        # user_role
        self.user_role_id_scope_ids = {}
        for scope_name in self.root_config['user_role_scopes']:
            scope_id = self.user_role_name_mapping[scope_name]
            self.user_role_id_scope_ids[scope_id] = set([
                self.scope_name_mapping[_scope_name] for _scope_name in self.root_config['user_role_scopes'][scope_name]
            ])

    def create_tables(self):
        SQLModel.metadata.create_all(self.db_engine)

    def jwt_encode(self, payload: dict):
        return jwt.encode(payload, self.jwt_secret_key, algorithm=self.jwt_algorithm)

    def jwt_decode(self, token: str):
        return jwt.decode(token, self.jwt_secret_key, algorithms=[self.jwt_algorithm])

    def send_email(self, recipient: Email, subject: str, body: str):

        print('''
Email sent to: {}
Subject: {}
Body: {}'''.format(recipient, subject, body))

    def send_sms(self, recipient: PhoneNumber, message: str):

        print('''
SMS sent to: {}
Message: {}'''.format(recipient, message))

    '''
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

        stale_event_ids = event.Event.find_ids(
            self.db[event.Event.COLLECTION_NAME], filter={'studio_id': {'$nin': list(studio_id_keys_by_id.keys())}})

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

        # groups
        # remove groups that reference events that no longer exist
        event_id_keys_by_id = event.Event.find_id_keys_by_id(
            self.db[event.Event.COLLECTION_NAME])

        stale_file_ids = media.Media.find_ids(
            self.db[media.Media.COLLECTION_NAME], filter={'event_id': {'$nin': list(event_id_keys_by_id.keys())}})

        print('Stale file ids')
        print(stale_file_ids)
        print()

        media.Media.delete_by_ids(
            self.db[media.Media.COLLECTION_NAME], list(stale_file_ids))

        # loop through existing events and update groups
        for event_id in event_id_keys_by_id:
            event_dict = event.Event.id_keys_to_dict(
                event_id_keys_by_id[event_id])

            event_dir = self.studios_dir.joinpath(studio_id_keys_by_id[event_dict['studio_id']][0]).joinpath(
                event.Event.build_directory_name(
                    {'datetime': event_dict['datetime'], 'name': event_dict['name']})
            )

            file_id_keys_to_add, file_ids_to_delete = media.Media.find_to_add_and_delete(
                self.db[media.Media.COLLECTION_NAME], event_dir, event_id)

            print(event_id)
            print(file_id_keys_to_add)
            print(file_ids_to_delete)

            for file_id_keys in file_id_keys_to_add:
                file_class = media.Media.get_media_type_from_id_keys(
                    file_id_keys)
                if file_class is None:
                    Warning('File ending not recognized {} not recognized on file {}'.format(
                        file_id_keys['file_ending'], file_id_keys))
                    continue
                new_file = file_class.make_from_id_keys(file_id_keys)
                new_file.insert(self.db[media.Media.COLLECTION_NAME])

            media.Media.delete_by_ids(
                self.db[media.Media.COLLECTION_NAME], list(file_ids_to_delete))
        '''
