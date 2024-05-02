import re
from pymongo import MongoClient
from gallery import config, databases, types
from gallery.objects.media.image import size
from gallery.objects import event
import datetime
# from gallery.objects.image import group, image, version
from pathlib import Path

# Initialize PyMongo
mongo_client = MongoClient(port=config.MONGODB_PORT)
db = mongo_client['gallery']

# read a local directory

ev = event.Event.load_from_db_collection_by_id(db['events'], 'a6Qo099EtWEG')
print(ev)
