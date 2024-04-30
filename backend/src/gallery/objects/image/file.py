from PIL import Image
import os
from src import types
from pathlib import Path
import pydantic


class ImageFile(pydantic.BaseModel):

    def model_post_init(self, _):
        self.path = Path()

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


class ImageFiles:
    pass
