import json
from pathlib import Path
import os
import typing
import yaml
from dotenv import dotenv_values
from gallery import types
from sqlmodel.ext.asyncio.session import AsyncSession as SQLMAsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker
import datetime as datetime_module
import isodate

SRC_DIR = Path(__file__).parent  # /gallery/backend/src/
BACKEND_DIR = SRC_DIR.parent  # /gallery/backend/
REPO_DIR = BACKEND_DIR.parent  # /gallery/

BACKEND_CONFIG_DIR = BACKEND_DIR / '.config'
BACKEND_DATA_DIR = BACKEND_DIR / 'data'
REPO_DATA_DIR = REPO_DIR / 'data'
SHARED_CONFIG_DIR = REPO_DIR / '.config'
REQUIREMENTS_INSTALLED_PATH = SRC_DIR / 'requirements_installed.txt'


def convert_env_path_to_absolute(root_dir: Path, a: str) -> Path:
    A = Path(a)
    if A.is_absolute():
        return A
    else:
        return (root_dir / A).resolve()


# THREE POSSIBLE ENV VARS

_app_env = os.getenv('APP_ENV', 'dev')  # default to dev
_shared_config_env_dir = os.getenv('SHARED_CONFIG_ENV_DIR')

if _shared_config_env_dir is None:
    SHARED_CONFIG_ENV_DIR = SHARED_CONFIG_DIR / _app_env
else:
    SHARED_CONFIG_ENV_DIR = convert_env_path_to_absolute(
        SRC_DIR, _shared_config_env_dir)

_backend_config_env_dir = os.getenv('BACKEND_CONFIG_ENV_DIR')
if _backend_config_env_dir is None:
    BACKEND_CONFIG_ENV_DIR = BACKEND_CONFIG_DIR / _app_env
else:
    BACKEND_CONFIG_ENV_DIR = convert_env_path_to_absolute(
        SRC_DIR, _backend_config_env_dir)


# Shared config

class SharedConfigEnv(typing.TypedDict):
    AUTH_KEY: str
    HEADER_KEYS: dict[str, str]
    FRONTEND_URLS: dict[str, str]
    SCOPE_NAME_MAPPING: dict[types.Scope.name, types.Scope.id]
    VISIBILITY_LEVEL_NAME_MAPPING: dict[types.VisibilityLevel.name,
                                        types.VisibilityLevel.id]
    PERMISSION_LEVEL_NAME_MAPPING: dict[types.PermissionLevel.name,
                                        types.PermissionLevel.id]
    USER_ROLE_NAME_MAPPING: dict[types.UserRole.name, types.UserRole.id]
    USER_ROLE_SCOPES: dict[types.UserRole.name, list[types.Scope.name]]
    OPENAPI_SCHEMA_PATH: str
    OTP_LENGTH: int
    GOOGLE_CLIENT_SECRET_PATH: str


SHARED_CONFIG_ENV_PATH = SHARED_CONFIG_ENV_DIR / 'config.yaml'

with SHARED_CONFIG_ENV_PATH.open('r') as f:
    _SHARED_CONFIG_ENV: SharedConfigEnv = yaml.safe_load(f)

# info from shared constants constants
AUTH_KEY: str = _SHARED_CONFIG_ENV['AUTH_KEY']
HEADER_KEYS: dict[str, str] = _SHARED_CONFIG_ENV['HEADER_KEYS']
FRONTEND_URLS: dict[str, str] = _SHARED_CONFIG_ENV['FRONTEND_URLS']

SCOPE_NAME_MAPPING: dict[types.Scope.name,
                         types.Scope.id] = _SHARED_CONFIG_ENV['SCOPE_NAME_MAPPING']
SCOPE_ID_MAPPING: dict[types.Scope.id, types.Scope.name] = {
    SCOPE_NAME_MAPPING[scope_name]: scope_name for scope_name in SCOPE_NAME_MAPPING
}

VISIBILITY_LEVEL_NAME_MAPPING: dict[types.VisibilityLevel.name,
                                    types.VisibilityLevel.id] = _SHARED_CONFIG_ENV['VISIBILITY_LEVEL_NAME_MAPPING']


PERMISSION_LEVEL_NAME_MAPPING: dict[types.PermissionLevel.name,
                                    types.PermissionLevel.id] = _SHARED_CONFIG_ENV['PERMISSION_LEVEL_NAME_MAPPING']

USER_ROLE_NAME_MAPPING: dict[types.UserRole.name,
                             types.UserRole.id] = _SHARED_CONFIG_ENV['USER_ROLE_NAME_MAPPING']

USER_ROLE_ID_SCOPE_IDS: dict[types.UserRole.id,
                             set[types.Scope.id]] = {
    USER_ROLE_NAME_MAPPING[user_role_name]: set([
        SCOPE_NAME_MAPPING[scope_name] for scope_name in _SHARED_CONFIG_ENV['USER_ROLE_SCOPES'][user_role_name]
    ]) for user_role_name in USER_ROLE_NAME_MAPPING
}

OPENAPI_SCHEMA_PATH = convert_env_path_to_absolute(
    SHARED_CONFIG_ENV_DIR, _SHARED_CONFIG_ENV['OPENAPI_SCHEMA_PATH'])

GOOGLE_CLIENT_SECRET = json.loads(convert_env_path_to_absolute(
    SHARED_CONFIG_ENV_DIR, _SHARED_CONFIG_ENV['GOOGLE_CLIENT_SECRET_PATH']).read_text())


# Backend Config


class DbEnv(typing.TypedDict):
    URL: str


CredentialNames = typing.Literal['access_token',
                                 'magic_link', 'request_sign_up', 'otp']


class AuthEnv(typing.TypedDict):
    credential_lifespans: dict[CredentialNames, types.ISO8601DurationStr]


class BackendConfigEnv(typing.TypedDict):
    URL: str
    UVICORN: dict
    DB: DbEnv
    MEDIA_DIR: str
    GOOGLE_CLIENT_PATH: str
    AUTH: AuthEnv


BACKEND_CONFIG_ENV_PATH = BACKEND_CONFIG_ENV_DIR / 'config.yaml'
BACKEND_SECRETS_ENV_PATH = BACKEND_CONFIG_ENV_DIR / 'secrets.env'


with BACKEND_CONFIG_ENV_PATH.open('r') as f:
    _BACKEND_CONFIG_ENV: BackendConfigEnv = yaml.safe_load(f)


def resolve_db_url(db_url: str, config_dir: Path) -> str:
    prefix = "sqlite+aiosqlite:///"
    abs_prefix = "sqlite+aiosqlite:////"
    if db_url.startswith(prefix) and not db_url.startswith(abs_prefix):
        # Relative path: resolve it
        db_file = db_url[len(prefix):]
        db_file_path = (config_dir / db_file).resolve()
        return f"{prefix}{db_file_path}"

    return db_url


db_url = _BACKEND_CONFIG_ENV['DB']['URL']
db_url = resolve_db_url(db_url, BACKEND_CONFIG_ENV_DIR)

DB_ASYNC_ENGINE = create_async_engine(_BACKEND_CONFIG_ENV['DB']['URL'])
ASYNC_SESSIONMAKER = async_sessionmaker(
    bind=DB_ASYNC_ENGINE,
    class_=SQLMAsyncSession,
    expire_on_commit=False
)

MEDIA_DIR = convert_env_path_to_absolute(
    BACKEND_CONFIG_ENV_DIR, _BACKEND_CONFIG_ENV['MEDIA_DIR'])

UVICORN = _BACKEND_CONFIG_ENV['UVICORN']


class AuthConfig(typing.TypedDict):
    credential_lifespans: dict[CredentialNames, datetime_module.timedelta]


AUTH: AuthConfig = {
    'credential_lifespans': {
        key: isodate.parse_duration(value) for key, value in _BACKEND_CONFIG_ENV['AUTH']['credential_lifespans'].items()
    }
}


class BackendSecrets(typing.TypedDict):
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    # GOOGLE_CLIENT_ID: str
    # GOOGLE_CLIENT_SECRET: str
    # GMAIL_USER: str
    # GMAIL_PASSWORD: str


BACKEND_SECRETS = typing.cast(
    BackendSecrets, dotenv_values(BACKEND_SECRETS_ENV_PATH))
