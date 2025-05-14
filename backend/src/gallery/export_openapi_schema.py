import json
from backend.src.gallery.app import app as fastapi_app
from backend.src.gallery import config

config.OPENAPI_SCHEMA_PATH.write_text(json.dumps(fastapi_app.openapi()))
