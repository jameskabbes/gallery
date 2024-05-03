import typing
from abc import ABC, abstractmethod
from gallery import types
from pymongo import collection


class Base:
    LOAD_INTO_EVENT_BY_FILENAME_KWARGS: typing.ClassVar = typing.TypedDict(
        'LOAD_INTO_EVENT_BY_FILENAME_KWARGS', {
            'db_collections': dict[str, collection.Collection],
            'filename': types.Filename,
            'event_id': types.EventId
        })


class ContentLoader(Base):

    id: types.DocumentId

    @classmethod
    @abstractmethod
    def load_basic_by_filenames(cls, filenames: list[types.Filename]) -> list[typing.Self]:
        """ Load the media by the filenames."""
