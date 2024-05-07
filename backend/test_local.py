import re
from gallery import config, types, utils
from gallery.objects import studios, events, medias


# Initialize PyMongo
mongo_client = utils.get_pymongo_client()
db = mongo_client['gallery']


try:
    print(studios.Studios.find(
        db[studios.Studios.COLLECTION_NAME]))

finally:
    mongo_client.close()
    pass
