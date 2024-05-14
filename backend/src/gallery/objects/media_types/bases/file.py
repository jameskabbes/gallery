from gallery import types
import pydantic
import typing
from abc import ABC, abstractmethod
from gallery.objects.media_types.bases import document_object as media_document_object


class Types:
    file_ending = types.FileEnding


class Base:
    FilenameIODict = typing.TypedDict('FilenameIODict', {})


class File(Base, pydantic.BaseModel, media_document_object.DocumentObject, ABC):
    file_ending: Types.file_ending
    ACCEPTABLE_FILE_ENDINGS: typing.ClassVar[types.AcceptableFileEndings] = {}

    @classmethod
    @abstractmethod
    def parse_filename(cls, filename: types.Filename) -> Base.FilenameIODict:
        """ Parse the filename into its defining keys."""

    @classmethod
    @abstractmethod
    def build_filename(cls, i_o_dict: Base.FilenameIODict) -> types.Filename:
        """ Build the filename from the defining keys."""
