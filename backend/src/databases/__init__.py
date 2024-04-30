from . import events, images, base
from pymongo import MongoClient
import typing
import types

DATABASE_MODULE = typing.Literal['events', 'images']

DATABASE_MODULES: dict[DATABASE_MODULE, types.ModuleType] = {
    'images': images,
    'events': events
}


def get_databases(mongo_client: MongoClient) -> dict[DATABASE_MODULE, base.Database]:

    d = {}
    for module in DATABASE_MODULES:
        database_class: base.Database = DATABASE_MODULES[module].Database
        d[module] = database_class.get_db(mongo_client)

    return d
