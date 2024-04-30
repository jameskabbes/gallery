from . import events, images, base
from pymongo import MongoClient
import typing


class TYPE_DATABASE_CLASSES(typing.TypedDict):
    images: images.Database
    events: events.Database


DATABASE_CLASSES: TYPE_DATABASE_CLASSES = {
    'images': images.Database,
    'events': events.Database
}


def get_databases(mongo_client: MongoClient) -> TYPE_DATABASE_CLASSES:

    d = {}
    for module in DATABASE_CLASSES:
        database_class: base.Database = DATABASE_CLASSES[module]
        d[module] = database_class(mongo_client)

    return d
