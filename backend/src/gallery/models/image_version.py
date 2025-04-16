from sqlmodel import Field, Relationship, select, SQLModel
from typing import TYPE_CHECKING, TypedDict, Optional, ClassVar
from pydantic import BaseModel
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import declared_attr
from .bases.table import Table as BaseTable
from .. import types
from . import file as file_module, gallery as gallery_module

ID_COL = 'id'

if TYPE_CHECKING:
    from . import image_file_metadata


class ImageVersionExport(BaseModel):
    id: types.ImageVersion.id
    base_name: types.ImageVersion.base_name | None
    parent_id: types.ImageVersion.parent_id | None
    version: types.ImageVersion.version | None
    datetime: types.ImageVersion.datetime | None
    description: types.ImageVersion.description | None
    aspect_ratio: types.ImageVersion.aspect_ratio | None
    average_color: types.ImageVersion.average_color | None


class ImageVersionImport(BaseModel):
    base_name: Optional[types.ImageVersion.base_name] = None
    parent_id: Optional[types.ImageVersion.parent_id] = None
    version: Optional[types.ImageVersion.version] = None
    datetime: Optional[types.ImageVersion.datetime] = None
    description: Optional[types.ImageVersion.description] = None


class ImageVersionUpdate(ImageVersionImport):
    id: types.ImageVersion.id
    pass


class ImageVersionAdminUpdate(ImageVersionUpdate):
    pass


class ImageVersionCreate (ImageVersionImport):
    pass


class ImageVersionAdminCreate(ImageVersionCreate):
    gallery_id: types.ImageVersion.gallery_id
    base_name: Optional[types.ImageVersion.base_name] = None
    version: Optional[types.ImageVersion.version] = None
    parent_id: Optional[types.ImageVersion.parent_id] = None
    datetime: Optional[types.ImageVersion.datetime] = None
    description: Optional[types.ImageVersion.description] = None
    aspect_ratio: Optional[types.ImageVersion.aspect_ratio] = None
    average_color: Optional[types.ImageVersion.average_color] = None


class ImageVersion(
        BaseTable[types.ImageVersion.id, ImageVersionAdminCreate,
                  ImageVersionAdminUpdate],
        table=True):

    __tablename__ = 'image_version'  # type: ignore

    id: types.ImageVersion.id = Field(
        primary_key=True, index=True, unique=True, const=True)
    base_name: types.ImageVersion.base_name = Field(
        nullable=True, index=True)
    parent_id: types.ImageVersion.parent_id = Field(
        nullable=True, index=True, foreign_key='image_version.' + ID_COL, ondelete='SET NULL')

    # BW, Edit1, etc. Original version is null
    version: types.ImageVersion.version = Field(nullable=True)
    gallery_id: types.ImageVersion.gallery_id = Field(
        index=True, foreign_key=str(gallery_module.Gallery.__tablename__) + '.' + gallery_module.ID_COL, ondelete='CASCADE')
    datetime: types.ImageVersion.datetime = Field(nullable=True)
    description: types.ImageVersion.description = Field(nullable=True)
    aspect_ratio: types.ImageVersion.aspect_ratio = Field(nullable=True)
    average_color: types.ImageVersion.average_color = Field(
        nullable=True)

    parent: Optional['ImageVersion'] = Relationship(
        back_populates='children', sa_relationship_kwargs={'remote_side': 'ImageVersion.id'})
    children: list['ImageVersion'] = Relationship(
        back_populates='parent')

    image_file_metadatas: list['image_file_metadata.ImageFileMetadata'] = Relationship(
        back_populates='version')
    gallery: 'gallery_module.Gallery' = Relationship(
        back_populates='image_versions')

    # @model_validator(mode='after')
    # def validate_model(self, info: ValidationInfo) -> None:
    #     if self.base_name is None and self.parent_id is None:
    #         raise ValueError('Unnamed versions must have a parent_id')

    # @field_validator('datetime')
    # @classmethod
    # def validate_datetime(cls, value: datetime_module.datetime, info: ValidationInfo) -> datetime_module.datetime:
    #     return validate_and_normalize_datetime(value, info)

    # @field_serializer('datetime')
    # def serialize_datetime(value: datetime_module.datetime) -> datetime_module.datetime:
    #     return value.replace(tzinfo=datetime_module.timezone.utc)

    # async def get_root_base_name(self) -> types.ImageVersion.base_name:
    #     if self.base_name is not None:
    #         return self.base_name
    #     else:
    #         if self.parent_id is not None:
    #             return (await self.parent.get_root_base_name())
    #         else:
    #             raise ValueError('Unnamed versions must have a parent_id')

    @classmethod
    def _build_select_by_id(cls, id):
        return select(cls).where(cls.id == id)
