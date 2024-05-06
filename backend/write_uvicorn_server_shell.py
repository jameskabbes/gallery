from gallery import config

if __name__ == '__main__':
    config.START_MONGODB_SERVER_PATH.write_text(
        'uvicorn app:app --reload --port {}'.format(
            config.UVICORN_PORT)
    )
