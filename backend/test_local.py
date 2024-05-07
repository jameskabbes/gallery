import re
from pymongo import MongoClient
from gallery import config, types, utils
from gallery.objects.media_types.image import file
from gallery.objects import event, studios as studios_module
import datetime
# from gallery.objects.image import group, image, version
from pathlib import Path


# Initialize PyMongo
mongo_client = utils.get_pymongo_client()
db = mongo_client[studios_module.Studios.DB_NAME]

studios = studios_module.Studios()
studios.load_studios(db[studios_module.Studios.COLLECTION_NAME])
print(studios)


try:
    pass
    # studios.load_studios(studios_module.Studios.get_collection(db))

finally:
    mongo_client.close()
    pass
