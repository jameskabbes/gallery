from src import config
import os

if __name__ == '__main__':

    # find where the mongodb dir is relative to the start_mongodb_server.sh
    common_prefix = os.path.commonprefix(
        [config.START_MONGODB_SERVER_PATH, config.MONGODB_DATA_DIR])

    relative_path = os.path.relpath(config.MONGODB_DATA_DIR, common_prefix)

    config.START_MONGODB_SERVER_PATH.write_text(
        'mongod --dbpath {} --port {}'.format(relative_path,
                                              config.MONGODB_PORT)
    )
