# Backend congif, edit with caution

import json
from gallery import types
from gallery.config import constants

BACKEND_DATA_DIR = constants.BACKEND_DIR / 'data'
REPO_DATA_DIR = constants.REPO_DIR / 'data'
PROJECT_SETTINGS_PATH = constants.REPO_DIR / 'settings.json'
PROJECT_CONSTANTS_PATH = constants.REPO_DIR / 'constants.json'

FASTAPI_RUN_PATH = constants.SRC_DIR / 'fastapi_run.sh'
FASTAPI_DEV_PATH = constants.SRC_DIR / 'fastapi_dev.sh'

REQUIREMENTS_INSTALLED_PATH = constants.SRC_DIR / 'requirements_installed.txt'

SHARED_SETTINGS = json.loads(PROJECT_SETTINGS_PATH.read_text())
SHARED_CONSTANTS = json.loads(PROJECT_CONSTANTS_PATH.read_text())

# info from constants
AUTH_KEY: str = SHARED_CONSTANTS['auth_key']
HEADER_KEYS: dict[str, str] = SHARED_CONSTANTS['header_keys']
FRONTEND_URLS: dict[str, str] = SHARED_CONSTANTS['frontend_urls']

SCOPE_NAME_MAPPING: dict[types.Scope.name,
                         types.Scope.id] = SHARED_CONSTANTS['scope_name_mapping']
SCOPE_ID_MAPPING: dict[types.Scope.id, types.Scope.name] = {
    SCOPE_NAME_MAPPING[scope_name]: scope_name for scope_name in SCOPE_NAME_MAPPING
}

VISIBILITY_LEVEL_NAME_MAPPING: dict[types.VisibilityLevel.name,
                                    types.VisibilityLevel.id] = SHARED_CONSTANTS['visibility_level_name_mapping']


PERMISSION_LEVEL_NAME_MAPPING: dict[types.PermissionLevel.name,
                                    types.PermissionLevel.id] = SHARED_CONSTANTS['permission_level_name_mapping']

USER_ROLE_NAME_MAPPING: dict[types.UserRole.name,
                             types.UserRole.id] = SHARED_CONSTANTS['user_role_name_mapping']

USER_ROLE_ID_SCOPE_IDS: dict[types.UserRole.id,
                             set[types.Scope.id]] = {
    USER_ROLE_NAME_MAPPING[user_role_name]: set([
        SCOPE_NAME_MAPPING[scope_name] for scope_name in SHARED_CONSTANTS['user_role_scopes'][user_role_name]
    ]) for user_role_name in USER_ROLE_NAME_MAPPING
}
