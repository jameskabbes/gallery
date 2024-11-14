from pathlib import Path
import json
from gallery import client
from main import app as fastapi_app

project_config = json.loads(client.PROJECT_CONFIG_PATH.read_text())
export_Path = Path(client.REPO_DIR, project_config['openapi_schema_path'])
export_Path.write_text(json.dumps(fastapi_app.openapi()))
