from PIL import Image
import os
from src import types
from pathlib import Path


class ImageFile(types.ImageFile):

    def __post_init__(self):
        super().__post_init__()

        self.path = Path()

        # Add extra initialization instructions
        print("Extra initialization in Child class")

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
