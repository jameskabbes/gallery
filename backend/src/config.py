from pathlib import Path

SRC_DIR = Path(__file__).parent
BACKEND_DIR = SRC_DIR.parent
REPO_DIR = BACKEND_DIR.parent
DATA_DIR = BACKEND_DIR / 'data'

PROJECT_CONFIG_PATH = REPO_DIR / 'config.json'
EXAMPLE_DATA_PATH = SRC_DIR / 'example_data.json'
START_MONGODB_SERVER_PATH = BACKEND_DIR / 'start_mongodb_server.sh'

IMAGES_DIR = DATA_DIR / 'images'

# Server
UVICORN_PORT = 8087

# MongoDB
MONGODB_DATA_DIR = DATA_DIR / 'db'
MONGODB_PORT = 27017

#
NANOID_ALPHABET = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
