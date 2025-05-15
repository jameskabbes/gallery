from sqlmodel.ext.asyncio.session import AsyncSession as SQLMAsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker
import json
from pathlib import Path
import os
import typing
import yaml
from dotenv import dotenv_values
import datetime as datetime_module
import isodate
from platformdirs import user_config_dir
import warnings
import secrets
from arbor_imago import custom_types, core_utils
import arbor_imago

ARBOR_IMAGO_DIR = Path(__file__).parent  # /gallery/backend/src/arbor_imago/
EXAMPLES_DIR = ARBOR_IMAGO_DIR / 'examples'
EXAMPLE_CONFIG_DIR = EXAMPLES_DIR / 'config'
EXAMPLE_BACKEND_CONFIG_DIR = EXAMPLE_CONFIG_DIR / 'backend'
EXAMPLE_SHARED_CONFIG_DIR = EXAMPLE_CONFIG_DIR / 'shared'
EXAMPLE_BACKEND_CONFIG_YAML_PATH = EXAMPLE_BACKEND_CONFIG_DIR / 'config.yaml'
EXAMPLE_BACKEND_SECRETS_ENV_PATH = EXAMPLE_BACKEND_CONFIG_DIR / 'secrets.env'
EXAMPLE_SHARED_CONFIG_YAML_PATH = EXAMPLE_SHARED_CONFIG_DIR / 'config.yaml'
SRC_DIR = ARBOR_IMAGO_DIR.parent
BACKEND_DIR = SRC_DIR.parent
REPO_DIR = BACKEND_DIR.parent

CONFIG_DIR = Path(user_config_dir(arbor_imago.__name__, appauthor=False))
if not CONFIG_DIR.exists():
    warnings.warn(
        'Config dir {} does not exist. Creating a new one.'.format(CONFIG_DIR))
    CONFIG_DIR.mkdir()


def convert_env_path_to_absolute(root_dir: Path, a: str) -> Path:
    A = Path(a)
    if A.is_absolute():
        return A
    else:
        return (root_dir / A).resolve()


# TWO POSSIBLE ENV VARS

_app_env = os.getenv('APP_ENV', None)
_config_env_dir = os.getenv('CONFIG_ENV_DIR', None)


if _config_env_dir is not None:
    CONFIG_ENV_DIR = convert_env_path_to_absolute(Path.cwd(), _config_env_dir)
elif _app_env is not None:
    CONFIG_ENV_DIR = CONFIG_DIR / _app_env
else:
    CONFIG_ENV_DIR = CONFIG_DIR / 'dev'
    warnings.warn(
        'Environment variables APP_ENV and CONFIG_ENV_DIR are not set. Defaulting to builtin dev environment located at {}.'.format(CONFIG_ENV_DIR))

if not CONFIG_ENV_DIR.exists():
    CONFIG_ENV_DIR.mkdir()
    warnings.warn(
        'Config env dir {} does not exist. Creating a new one.'.format(CONFIG_ENV_DIR))

BACKEND_CONFIG_ENV_DIR = CONFIG_ENV_DIR / 'backend'
SHARED_CONFIG_ENV_DIR = CONFIG_ENV_DIR / 'shared'


if not BACKEND_CONFIG_ENV_DIR.exists():
    BACKEND_CONFIG_ENV_DIR.mkdir()

if not SHARED_CONFIG_ENV_DIR.exists():
    SHARED_CONFIG_ENV_DIR.mkdir()


# Shared config

class SharedConfigEnv(typing.TypedDict):
    BACKEND_URL: str
    FRONTEND_URL: str
    AUTH_KEY: str
    HEADER_KEYS: dict[str, str]
    FRONTEND_ROUTES: dict[str, str]
    SCOPE_NAME_MAPPING: dict[custom_types.Scope.name, custom_types.Scope.id]
    VISIBILITY_LEVEL_NAME_MAPPING: dict[custom_types.VisibilityLevel.name,
                                        custom_types.VisibilityLevel.id]
    PERMISSION_LEVEL_NAME_MAPPING: dict[custom_types.PermissionLevel.name,
                                        custom_types.PermissionLevel.id]
    USER_ROLE_NAME_MAPPING: dict[custom_types.UserRole.name, custom_types.UserRole.id]
    USER_ROLE_SCOPES: dict[custom_types.UserRole.name, list[custom_types.Scope.name]]
    OPENAPI_SCHEMA_PATH: str
    OTP_LENGTH: int
    GOOGLE_CLIENT_SECRET_PATH: str


# generate these files if they do not exist


SHARED_CONFIG_ENV_PATH = SHARED_CONFIG_ENV_DIR / \
    EXAMPLE_SHARED_CONFIG_YAML_PATH.name
if not SHARED_CONFIG_ENV_PATH.exists():
    warnings.warn(
        'Shared config file {} does not exist. Creating a new one.'.format(SHARED_CONFIG_ENV_PATH))
    SHARED_CONFIG_ENV_PATH.write_text(
        EXAMPLE_SHARED_CONFIG_YAML_PATH.read_text())

BACKEND_CONFIG_ENV_YAML_PATH = BACKEND_CONFIG_ENV_DIR / \
    EXAMPLE_BACKEND_CONFIG_YAML_PATH.name
if not BACKEND_CONFIG_ENV_YAML_PATH.exists():
    warnings.warn(
        'Backend config file {} does not exist. Creating a new one.'.format(BACKEND_CONFIG_ENV_YAML_PATH))
    BACKEND_CONFIG_ENV_YAML_PATH.write_text(
        EXAMPLE_BACKEND_CONFIG_YAML_PATH.read_text())

BACKEND_CONFIG_ENV_SECRETS_PATH = BACKEND_CONFIG_ENV_DIR / \
    EXAMPLE_BACKEND_SECRETS_ENV_PATH.name
if not BACKEND_CONFIG_ENV_SECRETS_PATH.exists():
    warnings.warn(
        'Backend secrets file {} does not exist. Creating a new one.'.format(BACKEND_CONFIG_ENV_SECRETS_PATH))
    BACKEND_CONFIG_ENV_SECRETS_PATH.write_text(
        EXAMPLE_BACKEND_SECRETS_ENV_PATH.read_text().format(JWT_SECRET_KEY=core_utils.generate_jwt_secret_key()))

# read in the shared config file

with SHARED_CONFIG_ENV_PATH.open('r') as f:
    _SHARED_CONFIG_ENV: SharedConfigEnv = yaml.safe_load(f)


# info from shared constants constants
BACKEND_URL: str = _SHARED_CONFIG_ENV['BACKEND_URL']
FRONTEND_URL: str = _SHARED_CONFIG_ENV['FRONTEND_URL']
AUTH_KEY: str = _SHARED_CONFIG_ENV['AUTH_KEY']
HEADER_KEYS: dict[str, str] = _SHARED_CONFIG_ENV['HEADER_KEYS']
FRONTEND_ROUTES: dict[str, str] = _SHARED_CONFIG_ENV['FRONTEND_ROUTES']

SCOPE_NAME_MAPPING: dict[custom_types.Scope.name,
                         custom_types.Scope.id] = _SHARED_CONFIG_ENV['SCOPE_NAME_MAPPING']
SCOPE_ID_MAPPING: dict[custom_types.Scope.id, custom_types.Scope.name] = {
    SCOPE_NAME_MAPPING[scope_name]: scope_name for scope_name in SCOPE_NAME_MAPPING
}

VISIBILITY_LEVEL_NAME_MAPPING: dict[custom_types.VisibilityLevel.name,
                                    custom_types.VisibilityLevel.id] = _SHARED_CONFIG_ENV['VISIBILITY_LEVEL_NAME_MAPPING']


PERMISSION_LEVEL_NAME_MAPPING: dict[custom_types.PermissionLevel.name,
                                    custom_types.PermissionLevel.id] = _SHARED_CONFIG_ENV['PERMISSION_LEVEL_NAME_MAPPING']

USER_ROLE_NAME_MAPPING: dict[custom_types.UserRole.name,
                             custom_types.UserRole.id] = _SHARED_CONFIG_ENV['USER_ROLE_NAME_MAPPING']

USER_ROLE_ID_SCOPE_IDS: dict[custom_types.UserRole.id,
                             set[custom_types.Scope.id]] = {
    USER_ROLE_NAME_MAPPING[user_role_name]: set([
        SCOPE_NAME_MAPPING[scope_name] for scope_name in _SHARED_CONFIG_ENV['USER_ROLE_SCOPES'][user_role_name]
    ]) for user_role_name in USER_ROLE_NAME_MAPPING
}

OPENAPI_SCHEMA_PATH = convert_env_path_to_absolute(
    Path.cwd(), _SHARED_CONFIG_ENV['OPENAPI_SCHEMA_PATH'])

GOOGLE_CLIENT_SECRET = json.loads(convert_env_path_to_absolute(
    Path.cwd(), _SHARED_CONFIG_ENV['GOOGLE_CLIENT_SECRET_PATH']).read_text())

OTP_LENGTH: int = _SHARED_CONFIG_ENV['OTP_LENGTH']

# Backend Config


class DbEnv(typing.TypedDict):
    URL: str


CredentialNames = typing.Literal['access_token',
                                 'magic_link', 'request_sign_up', 'otp']


class AuthEnv(typing.TypedDict):
    credential_lifespans: dict[CredentialNames, custom_types.ISO8601DurationStr]


class BackendConfigEnv(typing.TypedDict):
    URL: str
    UVICORN: dict
    DB: DbEnv
    MEDIA_DIR: str
    GOOGLE_CLIENT_PATH: str
    AUTH: AuthEnv


with BACKEND_CONFIG_ENV_YAML_PATH.open('r') as f:
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


DB_ASYNC_ENGINE = create_async_engine(_BACKEND_CONFIG_ENV['DB']['URL'])
ASYNC_SESSIONMAKER = async_sessionmaker(
    bind=DB_ASYNC_ENGINE,
    class_=SQLMAsyncSession,
    expire_on_commit=False
)

MEDIA_DIR = convert_env_path_to_absolute(
    BACKEND_DIR, _BACKEND_CONFIG_ENV['MEDIA_DIR'])

GALLERIES_DIR = MEDIA_DIR / 'galleries'
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
    BackendSecrets, dotenv_values(BACKEND_CONFIG_ENV_SECRETS_PATH))
