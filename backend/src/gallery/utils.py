from pymongo import MongoClient, collection
import nanoid
from gallery import config


def get_unique_document_ids_from_collection(collection: collection.Collection) -> set:
    """Returns a unique document from a collection."""
    return set([item['_id'] for item in collection.find({}, {'_id': 1})])


def get_nanoid(alphabet: str = config.NANOID_ALPHABET, size: int = config.NANOID_SIZE) -> str:
    """Returns a nanoid."""
    return nanoid.generate(alphabet, size)
