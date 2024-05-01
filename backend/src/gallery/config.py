from pathlib import Path

GALLERY_DIR = Path(__file__).parent
SRC_DIR = GALLERY_DIR.parent
BACKEND_DIR = SRC_DIR.parent
REPO_DIR = BACKEND_DIR.parent
DATA_DIR = BACKEND_DIR / 'data'

PROJECT_CONFIG_PATH = REPO_DIR / 'config.json'
START_MONGODB_SERVER_PATH = BACKEND_DIR / 'start_mongodb_server.sh'

IMAGES_DIR = DATA_DIR / 'images'

# Server
UVICORN_PORT: int = 8087

# MongoDB
MONGODB_DATA_DIR = DATA_DIR / 'db'
MONGODB_PORT: int = 27017

# 1% change of collision at 1 Billion IDs
NANOID_ALPHABET: str = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
NANOID_SIZE: int = 12

ORIGINAL_KEY: str = '_original'
