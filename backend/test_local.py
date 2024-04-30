from pymongo import MongoClient
from src import config, databases
from src.objects import event

# Initialize PyMongo client
mongo_client = MongoClient(port=config.MONGODB_PORT)

mongo_databases = databases.get_databases(mongo_client)


wedding_collection = mongo_databases['images']['2023-11-17 Wedding']

image_document = wedding_collection.find_one({'_id': '0138'})
print(image_document)
