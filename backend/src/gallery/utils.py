from pymongo import MongoClient, collection
import nanoid
from gallery import config

# def generate_nanoid(alphabet: str = config.NANOID_ALPHABET, size: int = config.NANOID_SIZE) -> str:
#     """Returns a nanoid."""
#     return nanoid.generate(alphabet, size)


def deep_merge_dicts(primary_dict: dict, secondary_dict: dict) -> dict:
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``secondary_dict`` is merged into
    ``primary_dict``.
    :param primary_dict: dict onto which the merge is executed
    :param secondary_dict: primary_dict merged into primary_dict
    :return: None
    """
    for k in secondary_dict:
        if (k in primary_dict and isinstance(primary_dict[k], dict) and isinstance(secondary_dict[k], dict)):  # noqa
            deep_merge_dicts(primary_dict[k], secondary_dict[k])
        else:
            primary_dict[k] = secondary_dict[k]
    return primary_dict
