
from pathlib import Path
import json
from backend.src.app import app as fastapi_app
from backend.src import config

export_Path = Path(
    config.REPO_DIR, config.SHARED_CONSTANTS['openapi_schema_path'])
export_Path.write_text(json.dumps(fastapi_app.openapi()))
