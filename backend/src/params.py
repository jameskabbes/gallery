from pathlib import Path

SRC_DIR = Path(__file__).parent
BACKEND_DIR = SRC_DIR.parent
REPO_DIR = BACKEND_DIR.parent
DATA_DIR = BACKEND_DIR / 'Data'

PROJECT_CONFIG_PATH = REPO_DIR / 'config.json'

#
NANOID_ALPHABET = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
