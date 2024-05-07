from gallery import types, config, utils
from gallery.objects import studio as studio_module
from gallery.objects.db import collection_object
import typing
import pydantic
from pathlib import Path
from pymongo import collection


class Studios(pydantic.BaseModel, collection_object.CollectionObject[types.StudioId, studio_module.Studio]):
    COLLECTION_NAME: typing.ClassVar[str] = 'studios'
    CHILD_DOCUMENT_CLASS: typing.ClassVar = studio_module.Studio
    DIR: typing.ClassVar[Path] = config.STUDIOS_DIR
    PluralByIdType: typing.ClassVar = dict[types.StudioId,
                                           studio_module.Studio]

    studios: dict[types.StudioId, studio_module.Studio] = pydantic.Field(
        default_factory=dict)

    @classmethod
    def get_add_and_delete(cls, collection: collection.Collection) -> tuple[set[studio_module.Types.dir_name], dict[types.StudioId, studio_module.Studio]]:
        """Get the names of the studios to add to the database."""
        local_dir_names = cls.load_local_studio_dir_names()
        db_dir_names = set([item['dir_name'] for item in collection.find(
            {}, {config.DOCUMENT_ID_KEY: 0, 'dir_name': 1})])

        dir_names_to_add = local_dir_names - db_dir_names
        to_delete = db_dir_names - local_dir_names

        studios_ids_to_delete = cls.get_ids(
            collection, {'dir_name': {'$in': list(to_delete)}})

        return dir_names_to_add, studios_ids_to_delete

    @classmethod
    def load_local_studio_dir_names(cls) -> set[studio_module.Types.dir_name]:
        """Load the names of the studios from studios directory."""
        dir_names = set()
        if cls.DIR.exists():
            for subdir in cls.DIR.iterdir():
                if subdir.is_dir():
                    dir_names.add(subdir.name)
        return dir_names
