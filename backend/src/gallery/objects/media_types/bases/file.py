from gallery import types
import pydantic
import typing
from abc import ABC, abstractmethod


class Base:
    FilenameIODict = typing.TypedDict('FilenameIODict', {})


class File(Base, pydantic.BaseModel, ABC):

    id: types.DocumentId
    file_ending: types.FileEnding
    ACCEPTABLE_FILE_ENDINGS: typing.ClassVar[types.AcceptableFileEndings] = {}

    @classmethod
    @abstractmethod
    def parse_filename(cls, filename: types.Filename) -> Base.FilenameIODict:
        """ Parse the filename into its defining keys."""

    @classmethod
    @abstractmethod
    def build_filename(cls, i_o_dict: Base.FilenameIODict) -> types.Filename:
        """ Build the filename from the defining keys."""
