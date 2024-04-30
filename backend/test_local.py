from pymongo import MongoClient
from src import config, databases
from src.objects import event
from src.objects.image import group

# Initialize PyMongo
mongo_client = MongoClient(port=config.MONGODB_PORT)
mongo_databases = databases.get_databases(mongo_client)

#
event_wedding = event.Event(id='2023-11-17 Wedding')

a = group.ImageGroups.get_image_groups_ids(
    mongo_databases['images'].get_collection(event_wedding.id)
)
print(a)
