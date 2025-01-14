from pathlib import Path
import json
from gallery import types

GALLERY_DIR = Path(__file__).parent
SRC_DIR = GALLERY_DIR.parent
BACKEND_DIR = SRC_DIR.parent
BACKEND_DATA_DIR = BACKEND_DIR / 'data'
REPO_DIR = BACKEND_DIR.parent
REPO_DATA_DIR = REPO_DIR / 'data'
PROJECT_CONFIG_PATH = REPO_DIR / 'config.json'
PROJECT_CONSTANTS_PATH = REPO_DIR / 'constants.json'

FASTAPI_RUN_PATH = SRC_DIR / 'fastapi_run.sh'
FASTAPI_DEV_PATH = SRC_DIR / 'fastapi_dev.sh'

REQUIREMENTS_INSTALLED_PATH = SRC_DIR / 'requirements_installed.txt'

SHARED_CONFIG = json.loads(PROJECT_CONFIG_PATH.read_text())
SHARED_CONSTANTS = json.loads(PROJECT_CONSTANTS_PATH.read_text())


SCOPE_NAME_MAPPING: dict[types.ScopeTypes.name,
                         types.ScopeTypes.id] = SHARED_CONSTANTS['scope_name_mapping']
SCOPE_ID_MAPPING: dict[types.ScopeTypes.id, types.ScopeTypes.name] = {
    SCOPE_NAME_MAPPING[scope_name]: scope_name for scope_name in SCOPE_NAME_MAPPING
}

VISIBILITY_LEVEL_NAME_MAPPING: dict[types.VisibilityLevelTypes.name,
                                    types.VisibilityLevelTypes.id] = SHARED_CONSTANTS['visibility_level_name_mapping']


PERMISSION_LEVEL_NAME_MAPPING: dict[types.PermissionLevelTypes.name,
                                    types.PermissionLevelTypes.id] = SHARED_CONSTANTS['permission_level_name_mapping']

USER_ROLE_NAME_MAPPING: dict[types.UserRoleTypes.name,
                             types.UserRoleTypes.id] = SHARED_CONSTANTS['user_role_name_mapping']

USER_ROLE_ID_SCOPE_IDS: dict[types.UserRoleTypes.id,
                             set[types.ScopeTypes.id]] = {
    USER_ROLE_NAME_MAPPING[user_role_name]: set([
        SCOPE_NAME_MAPPING[scope_name] for scope_name in SHARED_CONSTANTS['user_role_scopes'][user_role_name]
    ]) for user_role_name in USER_ROLE_NAME_MAPPING
}
