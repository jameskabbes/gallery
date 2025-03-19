import typing
import pathlib
from gallery import utils, types
from gallery.config import settings
from sqlalchemy.ext.asyncio import AsyncSession as SQLAAsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL
import datetime
import json
from pathlib import Path
import jwt
import secrets

UvicornPortType = int


class UvicornConfig(typing.TypedDict):
    port: UvicornPortType


class DbConfig(typing.TypedDict):
    url: str | URL


class MediaRootConfig(typing.TypedDict):
    path: Path


class AuthenticationConfig(typing.TypedDict):
    stay_signed_in_default: bool
    expiry_timedeltas: dict[typing.Literal['access_token',
                                           'magic_link', 'request_sign_up', 'otp'], datetime.timedelta]


class JWTConfig(typing.TypedDict):
    secret_key_path: Path
    algorithm: str


class GoogleClientConfig(typing.TypedDict):
    path: Path


class Config(typing.TypedDict):
    uvicorn: UvicornConfig
    db: DbConfig
    media_root: MediaRootConfig
    authentication: AuthenticationConfig
    jwt: JWTConfig
    google_client: GoogleClientConfig

class OverrideConfig(typing.TypedDict, total=False):
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
        'url': f'sqlite+aiosqlite:///{settings.BACKEND_DATA_DIR / 'gallery.db'}',
    },
    'media_root': {
        'path': settings.BACKEND_DATA_DIR / 'media_root'
    },

    'authentication': {
        'stay_signed_in_default': False,
        'expiry_timedeltas': {
            'access_token': datetime.timedelta(days=7),
            'magic_link': datetime.timedelta(minutes=10),
            'request_sign_up': datetime.timedelta(hours=1),
            'otp': datetime.timedelta(minutes=10)
        }

    },
    'jwt': {
        'secret_key_path': settings.BACKEND_DATA_DIR / 'jwt_secret_key.txt',
        'algorithm': 'HS256'
    },
    'google_client': {
        'path': settings.REPO_DATA_DIR / 'google_client_secret.json'
    }
}


class Client:

    uvicorn_port: UvicornPortType
    AsyncSession: sessionmaker[SQLAAsyncSession]
    db_async_engine: AsyncEngine
    media_dir: pathlib.Path
    galleries_dir: pathlib.Path
    authentication: AuthenticationConfig
    jwt_secret_key: str
    jwt_algorithm: str
    google_client: dict

    def __init__(self, config: OverrideConfig = {}):

        merged_config: Config = utils.deep_merge_dicts(DefaultConfig, config)

        # uvicorn
        self.uvicorn_port = merged_config['uvicorn']['port']

        # db
        self.db_async_engine = create_async_engine(merged_config['db']['url'])
        self.AsyncSession = sessionmaker[SQLAAsyncSession](
            bind=self.db_async_engine,
            class_=SQLAAsyncSession,
            expire_on_commit=False
        )

        # media dir
        self.media_dir = merged_config['media_root']['path']

        if not self.media_dir.exists():
            self.media_dir.mkdir(parents=True)

        # galleries dir
        self.galleries_dir = self.media_dir / 'galleries'
        if not self.galleries_dir.exists():
            self.galleries_dir.mkdir(parents=True)

        # authentication
        self.authentication = merged_config['authentication']

        # jwt
        jwt_secret_key_path = merged_config['jwt']['secret_key_path']

        if not jwt_secret_key_path.exists():
            jwt_secret_key_path.write_text(self.generate_jwt_secret_key())

        self.jwt_secret_key = jwt_secret_key_path.read_text()
        self.jwt_algorithm = merged_config['jwt']['algorithm']

        # google client
        google_client_path = merged_config['google_client']['path']
        self.google_client = json.loads(google_client_path.read_text())

    def generate_jwt_secret_key(self):
        return secrets.token_hex(32)

    def jwt_encode(self, payload: dict) -> types.JwtEncodedStr:
        return jwt.encode(payload, self.jwt_secret_key, algorithm=self.jwt_algorithm)

    def jwt_decode(self, token: types.JwtEncodedStr) -> dict:
        return jwt.decode(token, self.jwt_secret_key, algorithms=[self.jwt_algorithm])

    def send_email(self, recipient: types.Email, subject: str, body: str):

        print('''
Email sent to: {}
Subject: {}
Body: {}'''.format(recipient, subject, body))

    def send_sms(self, recipient: types.PhoneNumber, message: str):

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
