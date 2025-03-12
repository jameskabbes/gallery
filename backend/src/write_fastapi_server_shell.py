from gallery import client
from gallery.config import settings

if __name__ == '__main__':

    c = client.Client()
    print(settings.FASTAPI_DEV_PATH)

    settings.FASTAPI_RUN_PATH.write_text(
        'fastapi run main.py --port {}'.format(
            c.uvicorn_port)
    )
    settings.FASTAPI_DEV_PATH.write_text(
        'fastapi dev main.py --port {}'.format(
            c.uvicorn_port)
    )
