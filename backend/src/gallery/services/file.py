from sqlmodel import Field, Relationship, select, SQLModel
from typing import TYPE_CHECKING, TypedDict, Optional, ClassVar
from pydantic import BaseModel

from .. import types, utils
from .bases import table, auth_credential
from . import gallery as gallery_module

if TYPE_CHECKING:
    from . import image_file_metadata

ID_COL = 'id'


class FileExport(BaseModel):
    id: types.File.id
    stem: types.File.stem
    suffix: types.File.suffix | None
    size: types.File.size


class FileImport(BaseModel):
    pass


class FileUpdate(FileImport):
    stem: Optional[types.File.stem] = None
    gallery_id: Optional[types.File.gallery_id] = None


class FileAdminUpdate(FileUpdate):
    pass


class FileCreate(FileImport):
    stem: types.File.stem
    suffix: types.File.suffix | None
    gallery_id: types.File.gallery_id
    size: types.File.size | None


class FileAdminCreate(FileCreate):
    pass


class File(
        table.Table[
            types.File.id,
            FileAdminCreate,
            FileAdminUpdate,
            table.AfterCreateCustomParams,
            table.AfterReadCustomParams,
            table.AfterUpdateCustomParams,
            table.AfterDeleteCustomParams],
        table=True):

    __tablename__ = 'file'  # type: ignore

    id: types.File.id = Field(
        primary_key=True, index=True, unique=True, const=True)
    stem: types.File.stem = Field()
    suffix: types.File.suffix = Field(nullable=True)
    gallery_id: types.File.gallery_id = Field(
        index=True, foreign_key=str(gallery_module.Gallery.__tablename__) + '.' + gallery_module.ID_COL, ondelete='CASCADE')
    size: types.File.size = Field(nullable=True)

    gallery: gallery_module.Gallery = Relationship(back_populates='files')
    image_file_metadata: Optional['image_file_metadata.ImageFileMetadata'] = Relationship(
        back_populates='file', cascade_delete=True)

    @property
    def name(self) -> str:
        return self.stem + ('' if self.suffix is None else self.suffix)

    @classmethod
    def _build_select_by_id(cls, id):
        return select(cls).where(cls.id == id)
