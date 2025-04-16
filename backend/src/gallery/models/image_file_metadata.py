from sqlmodel import Field, Relationship, select, SQLModel
from typing import TYPE_CHECKING, TypedDict, Optional, ClassVar
from pydantic import BaseModel
from sqlalchemy.ext.declarative import declared_attr

from .. import types
from .bases.table import Table as BaseTable
from . import file as file_module, image_version as image_version_module

# class ImageFileMetadataConfig:
#     _SUFFIXES: typing.ClassVar[set[str]] = {
#         '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}


# class ImageFileMetadataExport(TableExport):
#     file_id: types.ImageFileMetadata.file_id
#     version_id: types.ImageFileMetadata.version_id
#     scale: types.ImageFileMetadata.scale | None


class ImageFileMetadataImport(BaseModel):
    pass


class ImageFileMetadataUpdate(ImageFileMetadataImport):
    file_id: types.ImageFileMetadata.file_id


class ImageFileMetadataAdminUpdate(ImageFileMetadataUpdate):
    pass


class ImageFileMetadataCreate(ImageFileMetadataImport):
    file_id: types.ImageFileMetadata.file_id
    version_id: types.ImageFileMetadata.version_id
    scale: Optional[types.ImageFileMetadata.scale] = Field(
        default=None, ge=1, le=99)


class ImageFileMetadataAdminCreate(ImageFileMetadataCreate):
    pass


class ImageFileMetadata(
        BaseTable[types.ImageFileMetadata.file_id, ImageFileMetadataAdminCreate,
                  ImageFileMetadataAdminUpdate],
        table=True):

    __tablename__ = 'image_file_metadata'  # type: ignore

    file_id: types.ImageFileMetadata.file_id = Field(
        primary_key=True, index=True, unique=True, const=True, foreign_key=str(file_module.File.__tablename__) + '.' + file_module.ID_COL, ondelete='CASCADE')
    version_id: types.ImageFileMetadata.version_id = Field(
        index=True, foreign_key=str(image_version_module.ImageVersion.__tablename__) + '.' + image_version_module.ID_COL, ondelete='CASCADE')
    scale: Optional[types.ImageFileMetadata.scale] = Field(
        nullable=True, ge=1, le=99)

    version: 'image_version_module.ImageVersion' = Relationship(
        back_populates='image_file_metadatas')
    file: 'file_module.File' = Relationship(
        back_populates='image_file_metadata')

    # @classmethod
    # def parse_file_stem(cls, file_stem: str) -> tuple[types.ImageVersion.base_name, types.ImageVersion.version | None, types.ImageFileMetadata.scale | None]:

    #     scale = None
    #     if match := re.search(r'_(\d{2})$', file_stem):
    #         scale = int(match.group(1))
    #         file_stem = file_stem[:match.start()]

    #     version = None
    #     if match := re.search(r'_(.+)$', file_stem):
    #         version = match.group(1)
    #         file_stem = file_stem[:match.start()]

    #     return file_stem, version, scale

    # @classmethod
    # async def create(cls, params):
    #     return cls(
    #         params.create_model.model_dump()
    #     )

    @classmethod
    def _build_select_by_id(cls, id):
        return select(cls).where(cls.file_id == id)
