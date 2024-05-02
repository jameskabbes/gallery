from pymongo import database, collection, MongoClient
from gallery import types
from gallery.objects.media.image import group, size
from gallery.objects.media import media
import pydantic
import datetime as datetime_module
from pathlib import Path
import typing


class Types:
    id = types.EventId
    date = datetime_module.date
    name = str
    media = media.Media


class Init:
    id = Types.id
    date = Types.date | None
    name = Types.name
    media = Types.media


class Model(pydantic.BaseModel):
    id: Init.id = pydantic.Field(alias='_id')
    date: Init.date = pydantic.Field(
        default=None, exclude=True)
    name: Init.name = pydantic.Field(default=None, exclude=True)
    media: Init.media = pydantic.Field(default_factory=media.Media)

    class Config:
        _DIRECTORY_NAME_DELIM: str = ' '


class DirectoryNameContents(typing.TypedDict):
    date: Init.date
    name: Init.name


class Event(Model):

    @property
    def directory_name(self) -> str:
        return self.build_directory_name({'date': self.date, 'name': self.name})

    @staticmethod
    def parse_directory_name(directory_name: str) -> DirectoryNameContents:
        """Split the directory name into its defining keys."""
        args = directory_name.split(
            Model.Config._DIRECTORY_NAME_DELIM, 1)

        try:
            date = datetime_module.date.fromisoformat(args[0])
            name = args[1]
        except:
            date = None
            name = directory_name

        return {'date': date, 'name': name}

    @staticmethod
    def build_directory_name(d: DirectoryNameContents) -> str:

        directory_name = ''
        if d['date'] != None:
            directory_name += d['date'].isoformat()
            directory_name += types.Event.Config._DIRECTORY_NAME_DELIM
        directory_name += d['name']
        return directory_name

    # def add_image(self, image_file: size.Image):
    #     """Add an image file to the event."""
    #     if image_file.group_id not in self.image_groups:
    #         self.add_group(group.Group(id=image_file.group_id))
    #     self.image_groups[image_file.group_id].add_image(image_file)

    # def add_group(self, group: group.Group):
    #     self.image_groups[group.id] = group

    # def load_image_groups_from_directory(self, parent_path: Path):

    #     # load all files from the directory
    #     path = parent_path / self.id
    #     image_files = [f for f in path.iterdir() if f.is_file()]
    #     print('----------')
    #     print(image_files)

    #     for image_file in image_files:
    #         im = size.Image(
    #             **size.Image.id_to_defining_values(image_file.name))

    #         print(im)
    #         self.add_image(im)
    #         print(self.image_groups)
