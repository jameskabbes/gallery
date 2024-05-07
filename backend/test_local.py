import re
from gallery import config, types, utils
from gallery.objects import studios as studios_module, events as events_module, medias as medias_module


# Initialize PyMongo
mongo_client = utils.get_pymongo_client()
db = mongo_client['gallery']


try:
    print(studios_module.Studios.find(
        db[studios_module.Studios.COLLECTION_NAME]))

finally:
    mongo_client.close()
    pass
