from pathlib import Path

SRC_DIR = Path(__file__).parent
BACKEND_DIR = SRC_DIR.parent
DATA_DIR = BACKEND_DIR / 'Data'

FLASK_SECRET_KEY_PATH = DATA_DIR / 'flask_secret_key.txt'
