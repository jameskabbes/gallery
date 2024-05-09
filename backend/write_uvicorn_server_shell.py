from app import c
from gallery import config

if __name__ == '__main__':
    config.START_UVICORN_SERVER_PATH.write_text(
        'uvicorn app:app --reload --port {}'.format(
            c.uvicorn_port)
    )
