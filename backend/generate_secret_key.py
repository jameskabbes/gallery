from src import params
import secrets

params.FLASK_SECRET_KEY_PATH.write_text(secrets.token_hex(16))
