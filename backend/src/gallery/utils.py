from pymongo import MongoClient, collection


def get_unique_document_ids_from_collection(collection: collection.Collection) -> set:
    """Returns a unique document from a collection."""
    return set([item['_id'] for item in collection.find({}, {'_id': 1})])
