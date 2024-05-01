from pymongo import MongoClient
from gallery import config, databases
from gallery.objects import event
from gallery.objects.image import group, image, version
from pathlib import Path

# Initialize PyMongo
mongo_client = MongoClient(port=config.MONGODB_PORT)
mongo_databases = databases.get_databases(mongo_client)

#
# event.Event(
#    id='2023-11-18 Test').load_image_groups_from_directory(config.IMAGES_DIR)

a = image.Image(group_id='IMG_1234', version_id='BW',
                size_id='50', extension='jpg')
print(a)
a = image.Image(group_id='IMG_1234', extension='jpg')
print(a)

print(image.Image.id_to_defining_values(a.id))

event.Event(id='2023-11-18 Test').load_image_groups_from_directory(
    config.IMAGES_DIR)
