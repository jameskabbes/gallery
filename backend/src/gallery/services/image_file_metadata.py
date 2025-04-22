from sqlmodel import select
from ..models.tables import ImageFileMetadata as ImageFileMetadataTable
from . import base
from .. import types

from ..schemas import image_file_metadata as image_file_metadata_schema
from typing import ClassVar
import re


class ImageFileMetadata(
    base.Service[
        ImageFileMetadataTable,
        types.ImageFileMetadata.file_id,
        image_file_metadata_schema.ImageFileMetadataAdminCreate,
        image_file_metadata_schema.ImageFileMetadataAdminUpdate
    ],
        table=True):

    _TABLE = ImageFileMetadataTable

    SUFFIXES: ClassVar[set[str]] = {
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}

    @classmethod
    def table_id(cls, inst):
        return inst.file_id

    @classmethod
    def _build_select_by_id(cls, id):
        return select(cls._TABLE).where(cls._TABLE.file_id == id)

    @classmethod
    def parse_file_stem(cls, file_stem: str) -> tuple[types.ImageVersion.base_name, types.ImageVersion.version | None, types.ImageFileMetadata.scale | None]:

        scale = None
        if match := re.search(r'_(\d{2})$', file_stem):
            scale = int(match.group(1))
            file_stem = file_stem[:match.start()]

        version = None
        if match := re.search(r'_(.+)$', file_stem):
            version = match.group(1)
            file_stem = file_stem[:match.start()]

        return file_stem, version, scale
