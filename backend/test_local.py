import re
from pymongo import MongoClient
from gallery import config, databases, types
from gallery.objects.image import image
from gallery.objects import event
import datetime
# from gallery.objects.image import group, image, version
from pathlib import Path

# Initialize PyMongo
# mongo_client = MongoClient(port=config.MONGODB_PORT)
# db = mongo_client['gallery']

# read a local directory
ev = event.Event(_id='a6Qo099EtWEG', date=datetime.date(
    2023, 11, 17), name='Wedding')
print(ev.directory_name)
print('done')
