from sqlmodel import select

from gallery import types
from gallery.models.tables import File as FileTable
from gallery.schemas import file as file_schema
from gallery.services import base


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
