from src.databases import base
from src import types


class Database(base.Database):
    DATABASE_ID: str = 'events'
    COLLECTION_ID: types.EventId
