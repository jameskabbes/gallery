import typing
from gallery import types
from gallery import types, config
from gallery.objects.bases import document_object
from gallery.objects.media_types import base as base_file
import pydantic
import re


class Types:
    version = types.VersionId
    size = types.SizeId
    height = int
    width = int
    bytes = int
    average_color = types.HexColor

    ID_TYPES = base_file.Types.ID_TYPES | typing.Literal['version', 'size']
    ID_KEYS = base_file.Types.ID_KEYS + ('version', 'size')


class Base:
    _VERSION_DELIM: typing.ClassVar[str] = '-'
    _SIZE_BEG_TRIGGER: typing.ClassVar[str] = '('
    _SIZE_END_TRIGGER: typing.ClassVar[str] = ')'

    FILENAME_IO_KEYS: typing.ClassVar = (
        'name', 'version', 'size', 'file_ending')
    FilenameIODict = typing.TypedDict('FilenameIODict', {
        'name': str,
        'version': Types.version,
        'size': Types.size,
        'file_ending': base_file.Types.file_ending
    })


class File(Base, document_object.DocumentObject[types.ImageId, Types.ID_TYPES], base_file.File):

    version: Types.version | None = pydantic.Field(default=None)
    size: Types.size | None = pydantic.Field(default=None)
    height: Types.height | None = pydantic.Field(default=None)
    width: Types.width | None = pydantic.Field(default=None)
    bytes: Types.bytes | None = pydantic.Field(default=None)
    average_color: Types.average_color | None = pydantic.Field(default=None)

    # class vars
    ACCEPTABLE_FILE_ENDINGS: typing.ClassVar[types.AcceptableFileEndings] = {'jpg', 'jpeg', 'png', 'gif', 'cr2',
                                                                             'bmp', 'tiff', 'tif', 'ico', 'svg', 'webp', 'raw', 'heif', 'heic'}
    IDENTIFYING_KEYS: typing.ClassVar[tuple[Types.ID_TYPES]] = Types.ID_KEYS

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

    @pydantic.field_validator('version')
    def validate_version(cls, v):
        if v is not None and cls._VERSION_DELIM in v:
            raise ValueError('`version` must not contain "{}"'.format(
                cls._VERSION_DELIM))
        return v

    @ pydantic.field_validator('size')
    def validate_size(cls, v):
        if v is not None and (cls._SIZE_BEG_TRIGGER in v or cls._SIZE_END_TRIGGER in v):
            raise ValueError('`size` cannot contain "{}" or "{}"'.format(
                cls._SIZE_BEG_TRIGGER, cls._SIZE_END_TRIGGER))
        return v

    @ staticmethod
    def parse_filename(filename: types.Filename) -> Base.FilenameIODict:
        """Split the filename into its defining keys.

        IMG_1234-A(SM).jpg -> {'name': 'IMG_1234', 'version': 'A', 'size': 'SM', 'file_ending': 'jpg'}
        """

        d: Base.FilenameIODict = {
            'size': None,
            'version': None
        }

        args = filename.split('.', 1)
        if len(args) < 2:
            raise ValueError(
                'Missing file extension on filename "{}"'.format(filename))
        root, d['file_ending'] = args

        # get size
        last_beg_trigger = root.rfind(Base._SIZE_BEG_TRIGGER)
        if last_beg_trigger != -1:
            next_end_trigger = root[last_beg_trigger:].find(
                Base._SIZE_END_TRIGGER)

            if next_end_trigger != -1 and next_end_trigger == len(root)-last_beg_trigger-1:
                d['size'] = root[last_beg_trigger +
                                 1:next_end_trigger+last_beg_trigger]

                root = root[:last_beg_trigger]

        # get version
        args = root.rsplit(Base._VERSION_DELIM, 1)
        if len(args) == 2:
            d['version'] = args[-1]
        d['name'] = args[0]

        return d

    @ staticmethod
    def build_filename(d: Base.FilenameIODict) -> types.Filename:
        """Parse the id into its defining keys."""

        string: types.Filename = d['name']
        if d['version'] != None and d['version'] != config.ORIGINAL_KEY:
            string += f'{Base._VERSION_DELIM}{
                d["version"]}'
        if d['size'] != None and d['size'] != config.ORIGINAL_KEY:
            string += f'{Base._SIZE_BEG_TRIGGER}{Base._VERSION_DELIM}{
                d["size"]}{Base._SIZE_END_TRIGGER}'
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
