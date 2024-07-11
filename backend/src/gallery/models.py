from gallery import custom_types
from sqlmodel import Field, Session, SQLModel, select, column
import typing
import uuid

'''
class Singular[IDType]:

    _ID_COL: typing.ClassVar[str] = 'id'

    @classmethod
    def id_exists(cls, session: Session, id: IDType) -> bool:
        """check if a row with a given id exists in the database."""

        statement = select(getattr(cls, cls._ID_COL)
                           ).where(getattr(cls, cls._ID_COL) == id)
        results = session.exec(statement)
        return bool(results.one_or_none())

    @classmethod
    def get_from_db_by_id(cls, session: Session, id: IDType) -> typing.Self:
        return session.get(cls, id)
'''


class StudioBase(SQLModel):
    name: str


class Studio(StudioBase, table=True):
    id: custom_types.StudioID.__supertype__ = Field(
        primary_key=True, index=True)

    @classmethod
    def generate_id(cls):
        return custom_types.StudioID(str(uuid.uuid4()))


class StudioCreate(StudioBase):
    pass


class StudioUpdate(StudioBase):
    name: str | None = None


class StudioPublic(StudioBase):
    id: custom_types.StudioID
