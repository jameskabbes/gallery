from gallery import custom_types
import typing
import uuid
from sqlmodel import SQLModel, Field, Column


class Singular[IDType]:
    _ID_COL: typing.ClassVar[str] = 'id'

    @property
    def _id(self) -> IDType:
        return getattr(self, self._ID_COL)

# Studio


class StudioBase(SQLModel):
    name: str


class Studio(StudioBase, Singular, table=True):
    __tablename__ = 'studio'
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

# User
