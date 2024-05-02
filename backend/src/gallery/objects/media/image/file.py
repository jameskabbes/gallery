import typing
from gallery import types
from gallery import types, config
from gallery.objects.bases.document_object import DocumentObject
from gallery.objects.media.bases import file as base_file
import pydantic
import re


class Types:
    id = types.ImageId
    group_id = types.ImageGroupId
    file_ending = types.FileEnding
    version = types.ImageVersionId
    size = types.ImageSizeId
    height = int
    width = int
    bytes = int
    average_color = types.HexColor


class Init:
    id = Types.id
    group_id = Types.group_id
    file_ending = Types.file_ending
    version = Types.version | None
    size = Types.size | None
    height = Types.height | None
    width = Types.width | None
    bytes = Types.bytes | None
    average_color = Types.average_color | None


class Model(DocumentObject[Init.id]):

    group_id: Init.group_id
    file_ending: Init.file_ending

    version: Init.version = pydantic.Field(
        default=config.ORIGINAL_KEY)
    size: Init.size = pydantic.Field(
        default=config.ORIGINAL_KEY)
    height: Init.height = pydantic.Field(default=None)
    width: Init.width = pydantic.Field(default=None)
    bytes: Init.bytes = pydantic.Field(default=None)
    average_color: Init.average_color = pydantic.Field(default=None)

    @pydantic.field_validator('version')
    def validate_version(cls, v):
        if v is not None and cls.Config._VERSION_DELIM in v:
            raise ValueError('`version` must not contain "{}"'.format(
                cls.Config._VERSION_DELIM))
        return v

    @ pydantic.field_validator('size')
    def validate_size(cls, v):
        if v is not None and (cls.Config._SIZE_BEG_TRIGGER in v or cls.Config._SIZE_END_TRIGGER in v):
            raise ValueError('`size` cannot contain "{}" or "{}"'.format(
                cls.Config._SIZE_BEG_TRIGGER, cls.Config._SIZE_END_TRIGGER))
        return v

    @ pydantic.field_validator('height', 'width', 'bytes')
    def validate_positive(cls, v):
        if v is not None and v < 0:
            raise ValueError('must be None or greater than or equal to 0')
        return v

    @ pydantic.field_validator('average_color')
    def validate_average_color(cls, v):
        if v is not None and not re.match("^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$", v):
            raise ValueError('average_color must be a valid hex color or None')
        return v


class File(Model, base_file.File):

    class Config:
        ACCEPTABLE_FILE_ENDINGS = {'jpg', 'jpeg', 'png', 'gif', 'cr2',
                                   'bmp', 'tiff', 'tif', 'ico', 'svg', 'webp', 'raw', 'heif', 'heic'}

    @staticmethod
    def parse_filename(filename: Model.Config._FILENAME_TYPE) -> Model.Config.FilenameIODict:
        """Split the filename into its defining keys."""

        # IMG_1234-A(SM).jpg
        # IMG_1234-A.jpg
        # IMG_1234(SM).jpg
        # IMG_1234.jpg

        d: Model.Config.FilenameIODict = {
            'size': None,
            'version': None
        }

        a = d['version']
        a

        args = filename.split('.', 1)
        if len(args) < 2:
            raise ValueError(
                'Missing file extension on filename "{}"'.format(filename))
        root, d['file_ending'] = args

        # get size
        last_beg_trigger = root.rfind(Model.Config._SIZE_BEG_TRIGGER)
        if last_beg_trigger != -1:
            next_end_trigger = root[last_beg_trigger:].find(
                Model.Config._SIZE_END_TRIGGER)

            if next_end_trigger != -1 and next_end_trigger == len(root)-last_beg_trigger-1:
                d['size'] = root[last_beg_trigger +
                                 1:next_end_trigger+last_beg_trigger]

                root = root[:last_beg_trigger]

        # get version
        args = root.rsplit(Model.Config._VERSION_DELIM, 1)
        if len(args) == 2:
            d['version'] = args[-1]
        d['group_name'] = args[0]

        return d

    @staticmethod
    def build_filename(d: Model.Config.FilenameIODict) -> Model.Config._FILENAME_TYPE:
        """Parse the id into its defining keys."""

        string: Model.Config._FILENAME_TYPE = d['group_name']
        if d['version'] != None:
            string += f'{Model.Config._VERSION_DELIM}{
                d["version"]}'
        if d['size'] != None:
            string += f'{Model.Config._SIZE_BEG_TRIGGER}{Model.Config._VERSION_DELIM}{
                d["size"]}{Model.Config._SIZE_END_TRIGGER}'
        string += f'.{d["file_ending"]}'
        return string

    """
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
