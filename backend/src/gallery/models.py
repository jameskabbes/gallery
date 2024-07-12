from gallery import custom_types
from sqlmodel import Field, Session, SQLModel, select, column
import typing
import uuid


class Singular[IDType]:
    _ID_COL: typing.ClassVar[str] = 'id'


class StudioBase(SQLModel):
    name: str


class Studio(StudioBase, table=True):
    id: custom_types.StudioID.__value__ = Field(
        primary_key=True, index=True)

    @classmethod
    def generate_id(cls):
        return str(uuid.uuid4())


class StudioCreate(StudioBase):
    pass


class StudioUpdate(StudioBase):
    name: str | None = None


class StudioPublic(StudioBase):
    id: custom_types.StudioID
