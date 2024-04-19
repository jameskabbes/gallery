import pydantic
from src import types


class ImageVersion:
    id: types.Nanoid


class ImageGroup:
    id: types.Nanoid


class Album:
    pass

# a collection of albums


class Event:
    pass

# a collection of events / albums


class Gallery:
    pass


# a collection of galleries
class Studio:
    pass
