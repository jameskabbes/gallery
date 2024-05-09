from gallery import types, config, utils
from gallery.objects import studio as studio_module, events as events_module
from gallery.objects.db import collection_object
import typing
import pydantic
from pathlib import Path
from pymongo import collection, database


class Studios(pydantic.BaseModel, collection_object.CollectionObject[types.StudioId, studio_module.Studio]):
    COLLECTION_NAME: typing.ClassVar[str] = 'studios'
    CHILD_DOCUMENT_CLASS: typing.ClassVar = studio_module.Studio
    PluralByIdType: typing.ClassVar = dict[types.StudioId,
                                           studio_module.Studio]

    studios: dict[types.StudioId, studio_module.Studio] = pydantic.Field(
        default_factory=dict)
