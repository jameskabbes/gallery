from gallery.databases import base
from gallery import types


class Database(base.Database):
    DATABASE_ID: str = 'images'
    COLLECTION_ID: types.EventId
