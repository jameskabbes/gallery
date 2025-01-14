from pathlib import Path
import json
from gallery import client, config
from main import app as fastapi_app

export_Path = Path(
    config.REPO_DIR, config.SHARED_CONFIG['openapi_schema_path'])
export_Path.write_text(json.dumps(fastapi_app.openapi()))
