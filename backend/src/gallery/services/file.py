from sqlmodel import select
from ..models.tables import File as FileTable
from . import base
from .. import types

from ..schemas import file as file_schema


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
