import typing
import uuid
from sqlmodel import SQLModel, Field, Column, Session, select
from pydantic import BaseModel, EmailStr, constr, StringConstraints
from gallery import utils


class Singular[IDType]:
    _ID_COL: typing.ClassVar[str] = 'id'

    @property
    def _id(self) -> IDType:
        return getattr(self, self._ID_COL)

    @classmethod
    def generate_id(cls):
        return str(uuid.uuid4())

# Token


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


# User


class UserTypes:
    id = str
    username = typing.Annotated[str, StringConstraints(
        min_length=3, max_length=20)]
    email = typing.Annotated[EmailStr, StringConstraints(
        min_length=1, max_length=254)]
    password = typing.Annotated[str, StringConstraints(
        min_length=1, max_length=64)]
    hashed_password = str


class UserBase(BaseModel):
    username: UserTypes.username = Field(index=True)


class User(SQLModel, UserBase, Singular, table=True):
    __tablename__ = 'user'
    id: UserTypes.id = Field(
        primary_key=True, index=True)
    email: str = Field(index=True)
    hashed_password: UserTypes.hashed_password | None

    _payload_claim: typing.ClassVar[str] = 'sub'

    @classmethod
    def authenticate(cls, session: Session, username: str, password: str) -> typing.Self | None:
        user = session.exec(select(cls).where(
            cls.username == username)).first()

        if not user:
            return None
        if not utils.verify_password(password, user.hashed_password):
            return None
        return user

    def export_for_token_payload(self) -> dict:
        return {self._payload_claim: self.id}

    @classmethod
    def import_from_token_payload(self, token_payload: dict) -> UserTypes.id | None:
        return token_payload.get(self._payload_claim)


class UserCreate(BaseModel):
    username: UserTypes.username
    email: UserTypes.email
    password: UserTypes.password


class UserUpdate(UserBase):
    username: UserTypes.username | None = None
    email: UserTypes.email | None = None
    password: UserTypes.password | None = None


class UserPublic(UserBase):
    id: UserTypes.id


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
