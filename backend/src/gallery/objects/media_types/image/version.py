import pydantic
from gallery import types
from gallery.objects.media_types.image import file


class Version(pydantic.BaseModel):
    views: int = pydantic.Field(default=0)
    downloads: int = pydantic.Field(default=0)
    sizes: dict[types.SizeId, dict[types.FileEnding, file.File]] = pydantic.Field(
        default_factory=dict)

    def add_file(self, image_file: file.File):
        """Add file id to version"""

        if image_file.size not in self.sizes:
            self.sizes[image_file.size] = {}
        self.sizes[image_file.size][image_file.file_ending] = image_file.id
