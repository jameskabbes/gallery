from pathlib import Path
import json
from gallery.config import constants, settings
from main2 import app as fastapi_app

export_Path = Path(
    constants.REPO_DIR, settings.SHARED_SETTINGS['openapi_schema_path'])
export_Path.write_text(json.dumps(fastapi_app.openapi()))
