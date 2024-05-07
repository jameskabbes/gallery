from gallery import types, config, utils
from gallery.objects import studio as studio_module
from gallery.objects.db import collection_object
import typing
import pydantic
from pathlib import Path
from pymongo import collection


class Studios(pydantic.BaseModel, collection_object.CollectionObject[studio_module.Studio, types.StudioId]):
    COLLECTION_NAME: typing.ClassVar[str] = 'studios'
    CHILD_DOCUMENT_CLASS: typing.ClassVar = studio_module.Studio

    dir: Path = pydantic.Field(default=config.STUDIOS_DIR, exclude=True)
    studios: dict[types.StudioId, studio_module.Studio] = pydantic.Field(
        default_factory=dict)

    def load_studio_names_from_dir(self) -> set[studio_module.Types.dir_name]:
        """Load the names of the studios from the directory."""
        dir_names = set()
        if self.dir.exists():
            for subdir in self.dir.iterdir():
                if subdir.is_dir():
                    dir_names.add(subdir.name)
        return dir_names

    def load_studios(self, collection: collection.Collection):
        """Load the studios from the database or make new document."""
        local_dir_names = self.load_studio_names_from_dir()
        db_dir_names = set([i['dir_name'] for i in collection.find(
            {}, {config.DOCUMENT_ID_KEY: 0, 'dir_name': 1})])

        need_to_add = local_dir_names - db_dir_names
        need_to_delete = db_dir_names - local_dir_names

        for dir_name in local_dir_names:
            if dir_name in need_to_add:
                studio = studio_module.Studio(
                    _id=studio_module.Studio.generate_id(), dir_name=dir_name)
                studio.insert(collection)
            else:
                studio = studio_module.Studio(
                    **collection.find_one({'dir_name': dir_name}))
            print(studio)
            self.studios[studio.id] = studio
