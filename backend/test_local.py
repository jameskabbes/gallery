import re
from pymongo import MongoClient
from gallery import config, types
from gallery.objects.media.image import file
from gallery.objects import event
import datetime
# from gallery.objects.image import group, image, version
from pathlib import Path


image_file = file.File(_id='123', file_ending='jpg', group_id='123')

print(image_file)

"""

# Initialize PyMongo
mongo_client = MongoClient(port=config.MONGODB_PORT)
db = mongo_client['gallery']
events_collection = db['events']

try:

    # get all subfolders in images dir
    subfolders = [f for f in config.IMAGES_DIR.iterdir() if f.is_dir()]

    for subfolder in subfolders:
        event.Event.load_by_directory(db['events'], subfolder)


finally:
    mongo_client.close()


"""
