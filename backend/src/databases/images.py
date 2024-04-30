from src.databases import base
from src import types


class Database(base.Database):
    DATABASE_ID: str = 'images'
    COLLECTION_ID: types.EventId
