from pymongo import MongoClient
from gallery import config, databases
from gallery.objects import event
from gallery.objects.image import group, file, version
from pathlib import Path

# Initialize PyMongo
mongo_client = MongoClient(port=config.MONGODB_PORT)
mongo_databases = databases.get_databases(mongo_client)

#
# event.Event(
#    id='2023-11-18 Test').load_image_groups_from_directory(config.IMAGES_DIR)

a = file.File.from_filename('IMG_1234-BW-50.jpg')
print(a)
