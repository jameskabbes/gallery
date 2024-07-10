from pathlib import Path
import json
from gallery import config
from main import app as fastapi_app

project_config = json.loads(config.PROJECT_CONFIG_PATH.read_text())
export_Path = Path(config.REPO_DIR, project_config['openapi_schema_path'])
export_Path.write_text(json.dumps(fastapi_app.openapi()))
