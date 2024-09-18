from pathlib import Path

GALLERY_DIR = Path(__file__).parent
SRC_DIR = GALLERY_DIR.parent
BACKEND_DIR = SRC_DIR.parent
REPO_DIR = BACKEND_DIR.parent
DATA_DIR = BACKEND_DIR / 'data'
REPO_DATA_DIR = REPO_DIR / 'data'
DB_PATH = Path(DATA_DIR, 'softball.db')

PROJECT_CONFIG_PATH = REPO_DIR / 'config.json'
FASTAPI_RUN_PATH = SRC_DIR / 'fastapi_run.sh'
FASTAPI_DEV_PATH = SRC_DIR / 'fastapi_dev.sh'

REQUIREMENTS_INSTALLED_PATH = SRC_DIR / 'requirements_installed.txt'
