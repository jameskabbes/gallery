import json
from src.gallery.app import app as fastapi_app
from src.gallery import config

config.OPENAPI_SCHEMA_PATH.write_text(json.dumps(fastapi_app.openapi()))
