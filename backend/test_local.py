from pymongo import MongoClient
from src import config
from src.objects.event import Event, Events

# Initialize PyMongo client
mongo_client = MongoClient(port=config.MONGODB_PORT)

db_events = Events.get_db(mongo_client)

event_ids = Events.get_db_event_ids(db_events)
print(event_ids[0])
event = Event(id=event_ids[0])
print(event)
print(event.get_image_group_ids(db_events))
