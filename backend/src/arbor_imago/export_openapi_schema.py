import json
from src.arbor_imago.app import app as fastapi_app
from src.arbor_imago import config

config.OPENAPI_SCHEMA_PATH.write_text(json.dumps(fastapi_app.openapi()))
