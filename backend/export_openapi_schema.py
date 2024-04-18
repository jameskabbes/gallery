from pathlib import Path
import json
from src import params
from app import app as fastapi_app

project_config = json.loads(params.PROJECT_CONFIG_PATH.read_text())
export_Path = Path(params.REPO_DIR, project_config['openapi_schema_path'])
export_Path.write_text(json.dumps(fastapi_app.openapi()))
