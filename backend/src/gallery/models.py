import typing
import uuid
from sqlmodel import SQLModel, Field, Column, Session, select, delete, Relationship
from pydantic import BaseModel, EmailStr, constr, StringConstraints
from sqlalchemy import PrimaryKeyConstraint, and_
from gallery import utils
from abc import ABC, abstractmethod
import datetime as datetime_module
from enum import Enum
#


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class TokenData(BaseModel):
    username: str | None = None


class PermissionLevel(Enum):
    OWNER = 'owner'
    EDITOR = 'editor'
    VIEWER = 'viewer'


class VisibilityLevel(Enum):
    PUBLIC = 'public'
    PRIVATE = 'private'

#


class Table[IDType]:

    _ID_COLS: typing.ClassVar[list[str]] = ['id']

    @classmethod
    def generate_id(cls):
        return str(uuid.uuid4())

    @classmethod
    def get_by_id(cls, session: Session, id: IDType) -> typing.Self | None:

        if len(cls._ID_COLS) > 1:
            assert isinstance(id, (tuple, list))
            assert len(id) == len(cls._ID_COLS)
            return cls._get_by_key_values(session, {cls._ID_COLS[i]: id[i] for i in range(len(cls._ID_COLS))}).one_or_none()
        else:
            return cls._get_by_key_values(session, {cls._ID_COLS[0]: id}).one_or_none()

    @classmethod
    def get_by_key_value(cls, session: Session, key: str, value: typing.Any) -> list[typing.Self]:
        return cls._get_by_key_values(session, {key: value})

    @classmethod
    def _get_by_key_values(cls, session: Session, key_values: dict[str, typing.Any]):

        conditions = [getattr(cls, key) == value for key,
                      value in key_values.items()]

        query = select(cls).where(and_(*conditions))
        return session.exec(query)

    @classmethod
    def key_value_exists(cls, session: Session, key: str, value: typing.Any) -> bool:
        return cls.get_by_key_value(session, key, value) is not None

    def add_to_db(self, session: Session):
        session.add(self)
        session.commit()
        session.refresh(self)

    @classmethod
    def delete_by_id(cls, session: Session, id: IDType) -> bool:

        item = cls.get_by_id(session, id)
        if not item:
            return False

        session.delete(item)
        session.commit()
        return True

    def delete(self, session: Session) -> bool:
        return self.delete_by_id(session, getattr(self, self._ID_COL))

    @classmethod
    def not_found_message(cls) -> str:
        return f'{cls.__name__} not found'


class SingularCreate[TableType: Table](BaseModel):
    _SINGULAR_MODEL: typing.ClassVar[typing.Type[TableType]]

    def create(self) -> TableType:
        return self._SINGULAR_MODEL(
            **self.model_dump(),
            id=self._SINGULAR_MODEL.generate_id()
        )


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


class UserBase:
    _payload_claim: typing.ClassVar[str] = 'sub'

    def export_for_token_payload(self) -> dict:
        return {self._payload_claim: self.id}

    @classmethod
    def import_from_token_payload(self, token_payload: dict) -> UserTypes.id | None:
        return token_payload.get(self._payload_claim)


class User(SQLModel, Table[UserTypes.id], UserBase, table=True):
    __tablename__ = 'user'
    id: UserTypes.id = Field(primary_key=True, index=True)
    username: UserTypes.username = Field(index=True)
    email: UserTypes.email = Field(index=True)
    hashed_password: UserTypes.hashed_password | None

    @classmethod
    def authenticate(cls, session: Session, username: str, password: str) -> typing.Self | None:
        user = session.exec(select(cls).where(
            cls.username == username)).first()

        if not user:
            return None
        if not utils.verify_password(password, user.hashed_password):
            return None
        return user


class UserCreate(SingularCreate[User], UserBase):
    username: UserTypes.username
    email: UserTypes.email
    password: UserTypes.password

    _SINGULAR_MODEL: typing.ClassVar[typing.Type[User]] = User

    def create(self) -> User:
        return User(
            id=self._SINGULAR_MODEL.generate_id(),
            username=self.username,
            email=self.email,
            hashed_password=utils.hash_password(self.password))


class UserUpdate(BaseModel, UserBase):
    username: typing.Optional[UserTypes.username]
    email: typing.Optional[UserTypes.email]
    password: typing.Optional[UserTypes.password]


class UserPublic(BaseModel, UserBase):
    id: UserTypes.id
    username: UserTypes.username

    class Config:
        from_attributes = True


class UserPrivate(BaseModel, UserBase):
    id: UserTypes.id
    username: UserTypes.username
    email: UserTypes.email

    class Config:
        from_attributes = True

# Collection


class GalleryTypes:
    id = str
    name = typing.Annotated[str, StringConstraints(
        min_length=1, max_length=256)]
    visibility = VisibilityLevel
    parent_id = str  # GalleryTypes.id
    description = typing.Annotated[str, StringConstraints(
        min_length=1, max_length=20000)]
    datetime = datetime_module.datetime


class GalleryBase:
    pass


class Gallery(SQLModel, Table[GalleryTypes.id], GalleryBase, table=True):
    __tablename__ = 'gallery'
    id: GalleryTypes.id = Field(
        primary_key=True, index=True)
    name: GalleryTypes.name
    visibility: GalleryTypes.visibility = Field(VisibilityLevel.PUBLIC)
    parent_id: GalleryTypes.parent_id | None = Field(
        default=None, foreign_key=__tablename__ + '.id')
    description: GalleryTypes.name = Field(default='')
    datetime: GalleryTypes.datetime | None = Field(default=None)


class GalleryCreate(SingularCreate[GalleryBase], GalleryBase):
    name: GalleryTypes.name
    visibility: GalleryTypes.visibility
    parent_id: typing.Optional[GalleryTypes.parent_id]
    description: typing.Optional[GalleryTypes.description]
    datetime: typing.Optional[GalleryTypes.datetime]

    _SINGULAR_MODEL: typing.ClassVar[typing.Type[Gallery]] = Gallery


class GalleryUpdate(BaseModel, GalleryBase):
    name: typing.Optional[GalleryTypes.name]
    visibility: typing.Optional[GalleryTypes.visibility]
    parent_id: typing.Optional[GalleryTypes.parent_id]
    description: typing.Optional[GalleryTypes.description]
    datetime: typing.Optional[GalleryTypes.datetime]


class GalleryPublic(BaseModel, GalleryBase):

    id: GalleryTypes.id

    class Config:
        from_attributes = True


class GalleryPrivate(BaseModel, GalleryBase):

    id: GalleryTypes.id
    name: GalleryTypes.name
    parent_id: GalleryTypes.parent_id | None
    description: GalleryTypes.description | None
    datetime: GalleryTypes.datetime | None

    class Config:
        from_attributes = True


class GalleryPermission(SQLModel, Table[tuple[str, str]], table=True):

    __tablename__ = 'gallery_permission'
    __table_args__ = (
        PrimaryKeyConstraint('gallery_id', 'user_id'),
    )
    _ID_COLS: typing.ClassVar[list[str]] = ['gallery_id', 'user_id']

    gallery_id: GalleryTypes.id = Field(
        primary_key=True, index=True, foreign_key=Gallery.__tablename__ + '.id')
    user_id: UserTypes.id = Field(
        primary_key=True, index=True, foreign_key=User.__tablename__ + '.id')
    permission_level: PermissionLevel


if __name__ == '__main__':
    print()
