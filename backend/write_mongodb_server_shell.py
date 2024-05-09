from app import c
from gallery import config
import os

if __name__ == '__main__':

    # find where the mongodb dir is relative to the start_mongodb_server.sh
    common_prefix = os.path.commonprefix(
        [config.START_MONGODB_SERVER_PATH, c.pymongo_dir])

    # replace '\' with '/'
    relative_path = os.path.relpath(
        c.pymongo_dir, common_prefix).replace('\\', '/')

    config.START_MONGODB_SERVER_PATH.write_text(
        'mongod --dbpath {} --port {}'.format(relative_path,
                                              c.pymongo_port)
    )
