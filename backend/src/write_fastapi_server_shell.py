from gallery import config, get_client

c = get_client()

if __name__ == '__main__':

    print(config.FASTAPI_DEV_PATH)

    config.FASTAPI_RUN_PATH.write_text(
        'fastapi run main.py --port {}'.format(
            c.uvicorn_port)
    )
    config.FASTAPI_DEV_PATH.write_text(
        'fastapi dev main.py --port {}'.format(
            c.uvicorn_port)
    )
