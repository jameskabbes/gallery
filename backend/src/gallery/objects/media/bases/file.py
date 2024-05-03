from gallery import types
import pydantic
import typing


class File(pydantic.BaseModel):

    file_ending: types.FileEnding
    FILENAME_TYPE: typing.ClassVar[types.Filename]
    ACCEPTABLE_FILE_ENDINGS: typing.ClassVar[set[types.FileEnding]] = {}

    @classmethod
    def load_into_event_from_filename(cls, filename: types.Filename) -> typing.Self:
        pass
