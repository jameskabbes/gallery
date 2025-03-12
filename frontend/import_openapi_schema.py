import subprocess
import sys
import json
from pathlib import Path

project_settings = json.loads(Path('../settings.json').read_text())

COMMAND = ['npx', 'openapi-typescript', '../{}'.format(
    project_settings['openapi_schema_path']), '-o', './src/openapi_schema.d.ts']


def run_command():
    if sys.platform == "win32":
        # Windows-specific command
        subprocess.run(COMMAND, shell=True)
    else:
        # Unix/Linux/macOS-specific command
        subprocess.run(COMMAND)


if __name__ == "__main__":
    run_command()
