from gallery import types
import typing

FILENAME_TYPE = str
FILENAME_KEYS = ['group_name', 'version', 'size', 'file_ending']


class FilenameIODict(typing.TypedDict):
    group_name: types.ImageGroupTypes.name
    version: types.ImageInit.version
    size: types.ImageInit.size
    file_ending: types.ImageInit.file_ending


class Image:

    @staticmethod
    def parse_filename(filename: FILENAME_TYPE) -> FilenameIODict:
        """Split the filename into its defining keys."""

        # IMG_1234-A(SM).jpg
        # IMG_1234-A.jpg
        # IMG_1234(SM).jpg
        # IMG_1234.jpg

        d: FilenameIODict = {
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
        last_beg_trigger = root.rfind(types.Image.Config._SIZE_BEG_TRIGGER)
        if last_beg_trigger != -1:
            next_end_trigger = root[last_beg_trigger:].find(
                types.Image.Config._SIZE_END_TRIGGER)

            if next_end_trigger != -1 and next_end_trigger == len(root)-last_beg_trigger-1:
                d['size'] = root[last_beg_trigger +
                                 1:next_end_trigger+last_beg_trigger]

                root = root[:last_beg_trigger]

        # get version
        args = root.rsplit(types.Image.Config._VERSION_DELIM, 1)
        if len(args) == 2:
            d['version'] = args[-1]
        d['group_name'] = args[0]

        return d

    @staticmethod
    def build_filename(d: FilenameIODict) -> FILENAME_TYPE:
        """Parse the id into its defining keys."""

        string: FILENAME_TYPE = d['group_name']
        if d['version'] != None:
            string += f'{types.Image.Config._VERSION_DELIM}{
                d["version"]}'
        if d['size'] != None:
            string += f'{types.Image.Config._SIZE_BEG_TRIGGER}{types.Image.Config._VERSION_DELIM}{
                d["size"]}{types.Image.Config._SIZE_END_TRIGGER}'
        string += f'.{d["file_ending"]}'
        return string


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
