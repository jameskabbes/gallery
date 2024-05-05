from pymongo import MongoClient, collection
import nanoid
from gallery import config


def generate_nanoid(alphabet: str = config.NANOID_ALPHABET, size: int = config.NANOID_SIZE) -> str:
    """Returns a nanoid."""
    return nanoid.generate(alphabet, size)


def get_pymongo_client() -> MongoClient:
    """Returns a PyMongo client."""
    return MongoClient(port=config.MONGODB_PORT)
