from sqlmodel import select

from src.gallery import types
from src.gallery.models.tables import File as FileTable
from src.gallery.schemas import file as file_schema
from src.gallery.services import base


class File(
        base.Service[
            FileTable,
            types.File.id,
            file_schema.FileAdminCreate,
            file_schema.FileAdminUpdate,
        ],
        base.SimpleIdModelService[
            FileTable,
            types.File.id,
        ],
):
    _MODEL = FileTable

    @classmethod
    def model_name(cls, inst: FileTable) -> str:
        return inst.stem + ('' if inst.suffix is None else inst.suffix)
