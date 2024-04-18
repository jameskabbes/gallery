import subprocess
import sys
import json
from pathlib import Path

project_config = json.loads(Path('../config.json').read_text())

COMMAND = 'npx openapi-typescript ../{} -o ./src/openapi_schema.d.ts'.format(
    project_config['openapi_schema_path'])


def run_command():
    if sys.platform == "win32":
        # Windows-specific command
        subprocess.run(COMMAND, shell=True)
    else:
        # Unix/Linux/macOS-specific command
        subprocess.run(COMMAND)


if __name__ == "__main__":
    run_command()
