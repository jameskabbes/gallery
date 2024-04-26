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
        # Get the file size
        file_size = os.path.getsize(image_path)
        print("File Size:", file_size, "bytes")

    def get_shape(image_path):
        # Open the image
        with Image.open(image_path) as img:
            # Get the dimensions (shape) of the image
            width, height = img.size
            print("Image Shape (Width x Height):", width, "x", height)
