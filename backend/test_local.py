import re
from pymongo import MongoClient
from gallery import config, types, utils
from gallery.objects.media.image import file
from gallery.objects import event, studio as studio_module
import datetime
# from gallery.objects.image import group, image, version
from pathlib import Path


# Initialize PyMongo
mongo_client = utils.get_pymongo_client()
studio = studio_module.Studio(
    _id=studio_module.Studio._id, mongo_client=mongo_client)


try:
    print(studio)


finally:
    mongo_client.close()
    pass
