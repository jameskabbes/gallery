from gallery import custom_types
from sqlmodel import Field, Session, SQLModel
import pydantic

from sqlmodel import Field, Session, SQLModel, select, column
import typing


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

    """
    def add_to_db(self, session: Session, commit_and_close: bool = True):
        session.add(self)

        if commit_and_close:
            session.commit()
            session.close()
    """


class Plural[IDType]:
    pass


class Studio(SQLModel, Singular[custom_types.StudioID], table=True):
    id: custom_types.StudioID.__value__ = Field(primary_key=True, index=True)
    name: str
    test: int | None
