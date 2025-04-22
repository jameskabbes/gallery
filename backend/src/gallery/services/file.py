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
        table=True):

    _TABLE = FileTable

    @classmethod
    def table_id(cls, inst):
        return inst.id

    @classmethod
    def table_name(cls, inst: FileTable) -> str:
        return inst.stem + ('' if inst.suffix is None else inst.suffix)

    @classmethod
    def _build_select_by_id(cls, id):
        return select(cls._TABLE).where(cls._TABLE.id == id)
