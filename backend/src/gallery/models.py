import typing
import uuid
from sqlmodel import SQLModel, Field, Column


class Singular[IDType]:
    _ID_COL: typing.ClassVar[str] = 'id'

    @property
    def _id(self) -> IDType:
        return getattr(self, self._ID_COL)

    @classmethod
    def generate_id(cls):
        return str(uuid.uuid4())


# Studio

class StudioTypes:
    id = str
    name = str


class StudioBase(SQLModel):
    name: StudioTypes.name


class Studio(StudioBase, Singular, table=True):
    __tablename__ = 'studio'
    id: StudioTypes.id = Field(
        primary_key=True, index=True)


class StudioCreate(StudioBase):
    pass


class StudioUpdate(StudioBase):
    name: StudioTypes.name | None = None


class StudioPublic(StudioBase):
    id: StudioTypes.id

# User


class UserTypes:
    id = str
    username = str
    email = str
    password = str
    hashed_password = str


class UserBase(SQLModel):
    username: str = Field(index=True)


class User(UserBase, Singular, table=True):
    __tablename__ = 'user'
    id: UserTypes.id = Field(
        primary_key=True, index=True)
    email: str = Field(index=True)
    hashed_password: UserTypes.hashed_password | None


class UserCreate(UserBase):
    username: UserTypes.username
    email: UserTypes.email
    password: UserTypes.password


class UserUpdate(UserBase):
    username: UserTypes.username | None = None
    email: UserTypes.email | None = None
    password: UserTypes.password | None = None


class UserPublic(UserBase):
    id: UserTypes.id
