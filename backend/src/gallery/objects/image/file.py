from PIL import Image
import os
from pathlib import Path
from gallery import types
import pydantic
import typing


class File(pydantic.BaseModel):

    group_id: types.ImageGroupId
    version_id: types.ImageVersionId | None = pydantic.Field(
        default=None)
    size_id: types.ImageSizeId | None = pydantic.Field(
        default=None)
    extension: str

    class Config:
        _DELIM = '-'

    @property
    def filename(self) -> str:
        """build and return the filename property from self's attributes."""
        string = self.group_id
        if self.version_id:
            string += f'{File.Config._DELIM}{self.version_id}'
        if self.size_id:
            string += f'{File.Config._DELIM}{self.size_id}'
        string += f'.{self.extension}'
        return string

    @classmethod
    def from_filename(cls, filename: str) -> typing.Self:

        group_id, version_id, size_id, extension = File.parse_filename(
            filename)
        return File(group_id=group_id, version_id=version_id, size_id=size_id, extension=extension)

    @staticmethod
    def parse_filename(filename) -> tuple[types.ImageGroupId, types.ImageVersionId, types.ImageSizeId, str]:
        """Parse the filename into its components."""

        # IMG_1234-BW-50.jpg
        # IMG_1234.jpg
        # IMG_1234-50.jpg

        args = filename.split('.', 1)

        if len(args) != 2:
            raise MissingFileExtension(filename)

        root, extension = args

        items = root.split(File.Config._DELIM, 2)
        group_id = items[0]
        version_id = None
        size_id = None

        if len(items) >= 2:
            size_id = items[-1]

            if len(items) == 3:
                version_id = items[1]

        return group_id, version_id, size_id, extension

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


class MissingFileExtension(Exception):

    MESSAGE = 'Missing file extension on filename "{}"'

    def __init__(self, filename):
        super().__init__(self.MESSAGE.format(filename))
