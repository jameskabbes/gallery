from pathlib import Path

GALLERY_DIR = Path(__file__).parent
SRC_DIR = GALLERY_DIR.parent
BACKEND_DIR = SRC_DIR.parent
REPO_DIR = BACKEND_DIR.parent
DATA_DIR = BACKEND_DIR / 'data'

PROJECT_CONFIG_PATH = REPO_DIR / 'config.json'

START_UVICORN_SERVER_PATH = BACKEND_DIR / 'start_uvicorn_server.sh'
START_MONGODB_SERVER_PATH = BACKEND_DIR / 'start_mongodb_server.sh'

ORIGINAL_KEY: str = '_original'
DOCUMENT_ID_KEY: str = '_id'

NANOID_ALPHABET: str = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
NANOID_SIZE: int = 12
