from typing import TypedDict
from PIL import Image as PIL_Image
import os
from pathlib import Path
from gallery import types
import pydantic
import typing


class ImageBase(types.Image):

    class Config:
        _DELIM = '-'
        DEFINING_KEYS = ['group_id', 'version_id', 'size_id', 'extension']
        DEFINING_DICT = TypedDict('DEFINING_DICT', {
            'group_id': types.Image.__annotations__['group_id'],
            'version_id': types.Image.__annotations__['version_id'],
            'size_id': types.Image.__annotations__['size_id'],
            'extension': types.Image.__annotations__['extension']
        })


class Image(ImageBase):

    @pydantic.root_validator(pre=True)
    def generate_id(cls, values):

        values['id'] = Image.id_from_defining_values(
            {key: values[key] if key in values else None for key in Image.Config.DEFINING_KEYS})
        return values

    @staticmethod
    def id_from_defining_values(defining_dict: ImageBase.Config.DEFINING_DICT) -> types.Image.__annotations__['id']:
        """Generate the id from its components."""

        string = defining_dict['group_id']
        if defining_dict['version_id']:
            string += f'{Image.Config._DELIM}{defining_dict["version_id"]}'
        if defining_dict['size_id']:
            string += f'{Image.Config._DELIM}{defining_dict["size_id"]}'
        string += f'.{defining_dict["extension"]}'
        return string

    @staticmethod
    def id_to_defining_values(id: types.ImageId) -> ImageBase.Config.DEFINING_DICT:
        """Parse the id into its defining keys."""

        # IMG_1234-BW-50.jpg
        # IMG_1234.jpg
        # IMG_1234-50.jpg

        defining_dict: Image.Config.DEFINING_DICT = {}

        args = id.split('.', 1)

        if len(args) != 2:
            raise MissingFileExtension(id)

        root, extension = args

        items = root.split(Image.Config._DELIM, 2)
        defining_dict['group_id'] = items[0]
        defining_dict['extension'] = extension
        defining_dict['size_id'] = None
        defining_dict['version_id'] = None

        if len(items) >= 2:
            defining_dict['size_id'] = items[-1]

            if len(items) == 3:
                defining_dict['version_id'] = items[1]

        return defining_dict


"""
class File:
    pass

    def get_shape(self):
        pass

    def get_size(self):
        self.bytes = os.stat(self.path).st_size

    def get_shape(self):
        img = Image.open(self.path)
        self.width, self.height = img.size

    def get_average_color(self):
        img = Image.open(self.path)
        img = img.convert('RGB')

        r, g, b = 0, 0, 0
        pixels = img.load()
"""


class MissingFileExtension(Exception):

    MESSAGE = 'Missing file extension on filename "{}"'

    def __init__(self, filename):
        super().__init__(self.MESSAGE.format(filename))
