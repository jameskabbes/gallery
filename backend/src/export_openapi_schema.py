import json
from src.app import app as fastapi_app
from src import config

config.OPENAPI_SCHEMA_PATH.write_text(json.dumps(fastapi_app.openapi()))
