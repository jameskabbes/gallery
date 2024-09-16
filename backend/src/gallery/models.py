import typing
import uuid
from sqlmodel import SQLModel, Field, Column, Session, select, delete, Relationship
from pydantic import BaseModel, EmailStr, constr, StringConstraints
from sqlalchemy import PrimaryKeyConstraint, and_, or_
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
    VIEWER = 'viewer'
    EDITOR = 'editor'
    OWNER = 'owner'

    def __lt__(self, other):
        order = ['viewer', 'editor', 'owner']
        if self.__class__ is other.__class__:
            return order.index(self.value) < order.index(other.value)
        return NotImplemented

    def __le__(self, other):
        return self < other or self == other

    def __gt__(self, other):
        return not self <= other

    def __ge__(self, other):
        return not self < other


class VisibilityLevel(Enum):
    PUBLIC = 'public'
    PRIVATE = 'private'

#


class Table[IDType]:

    _ID_COLS: typing.ClassVar[list[str]] = ['id']

    @property
    def _id(self) -> IDType:
        """Return the ID of the model"""

        if len(self._ID_COLS) > 1:
            return tuple(getattr(self, key) for key in self._ID_COLS)
        else:
            return getattr(self, self._ID_COLS[0])

    @classmethod
    def generate_id(cls):
        """Generate a new ID for the model"""

        return str(uuid.uuid4())

    @classmethod
    def get_one_by_id(cls, session: Session, id: IDType) -> typing.Self | None:
        """Get a model by its ID"""

        if len(cls._ID_COLS) > 1:
            assert isinstance(id, (tuple, list))
            assert len(id) == len(cls._ID_COLS)
            return cls._get_by_key_values(session, {cls._ID_COLS[i]: id[i] for i in range(len(cls._ID_COLS))}).one_or_none()
        else:
            return cls._get_by_key_values(session, {cls._ID_COLS[0]: id}).one_or_none()

    @classmethod
    def get_one_by_key_values(cls, session: Session, key_values: dict[str, typing.Any]) -> typing.Self | None:
        """Get a model by its key values"""
        return cls._get_by_key_values(session, key_values).one_or_none()

    @classmethod
    def get_all_by_key_values(cls, session: Session, key_values: dict[str, typing.Any]) -> list[typing.Self]:
        """Get all models by their key values"""
        return cls._get_by_key_values(session, key_values).all()

    @classmethod
    def _get_by_key_values(cls, session: Session, key_values: dict[str, typing.Any]):

        conditions = [getattr(cls, key) == value for key,
                      value in key_values.items()]

        query = select(cls).where(and_(*conditions))
        return session.exec(query)

    def add_to_db(self, session: Session):
        """Add the model to the database"""

        session.add(self)
        session.commit()
        session.refresh(self)

    @classmethod
    def delete_one_by_id(cls, session: Session, id: IDType) -> int:
        """Delete a model by its ID"""

        return cls.delete_many_by_ids(session, [id])

    @classmethod
    def delete_many_by_ids(cls, session: Session, ids: list[typing.Any]) -> int:
        """Delete models by their IDs"""

        if len(cls._ID_COLS) > 1:
            conditions = [and_(*[getattr(cls, cls._ID_COLS[i]) == id[i]
                               for i in range(len(cls._ID_COLS))]) for id in ids]
        else:
            conditions = [getattr(cls, cls._ID_COLS[0]) == id for id in ids]

        query = delete(cls).where(or_(*conditions))
        result = session.exec(query)
        session.commit()
        return result.rowcount

    @classmethod
    def not_found_message(cls) -> str:
        return f'{cls.__name__} not found'

    @classmethod
    async def is_available(cls, session: Session) -> bool:
        return True


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
    email = typing.Annotated[EmailStr, StringConstraints(
        min_length=1, max_length=254)]
    password = typing.Annotated[str, StringConstraints(
        min_length=1, max_length=64)]
    username = typing.Annotated[str, StringConstraints(
        min_length=3, max_length=20)]
    hashed_password = str


class UserBase:
    _payload_claim: typing.ClassVar[str] = 'sub'

    def export_for_token_payload(self) -> dict:
        return {self._payload_claim: self.id}

    @classmethod
    def import_from_token_payload(self, token_payload: dict) -> UserTypes.id | None:
        return token_payload.get(self._payload_claim)


class UserUpdate(BaseModel, UserBase):
    email: typing.Optional[UserTypes.email] = None
    password: typing.Optional[UserTypes.password] = None
    username: typing.Optional[UserTypes.username] = None


class UserPublic(BaseModel, UserBase):
    id: UserTypes.id
    username: UserTypes.username | None

    class Config:
        from_attributes = True


class UserPrivate(BaseModel, UserBase):
    id: UserTypes.id
    email: UserTypes.email
    username: UserTypes.username | None

    class Config:
        from_attributes = True


class User(SQLModel, Table[UserTypes.id], UserBase, table=True):
    __tablename__ = 'user'
    id: UserTypes.id = Field(primary_key=True, index=True, unique=True)
    email: UserTypes.email = Field(index=True, unique=True)
    username: UserTypes.username = Field(
        index=True, unique=True, nullable=True, default=None)
    hashed_password: UserTypes.hashed_password | None

    @classmethod
    def authenticate(cls, session: Session, email: str, password: str) -> typing.Self | None:

        user = cls.get_one_by_key_values(session, {'email': email})
        if not user:
            return None
        if not utils.verify_password(password, user.hashed_password):
            return None
        return user


class UserCreate(SingularCreate[User], UserBase):
    email: UserTypes.email
    password: UserTypes.password

    _SINGULAR_MODEL: typing.ClassVar[typing.Type[User]] = User

    def create(self) -> User:
        return User(
            id=self._SINGULAR_MODEL.generate_id(),
            email=self.email,
            hashed_password=utils.hash_password(self.password))


# Collection


class GalleryTypes:
    id = str
    name = typing.Annotated[str, StringConstraints(
        min_length=1, max_length=256)]
    visibility = VisibilityLevel
    parent_id = str  # GalleryTypes.id
    description = typing.Annotated[str, StringConstraints(
        min_length=1, max_length=20000)]
    date = datetime_module.date


class GalleryBase:
    pass


class GalleryUpdate(BaseModel, GalleryBase):
    name: typing.Optional[GalleryTypes.name] = None
    visibility: typing.Optional[GalleryTypes.visibility] = None
    parent_id: typing.Optional[GalleryTypes.parent_id] = None
    description: typing.Optional[GalleryTypes.description] = None
    date: typing.Optional[GalleryTypes.date] = None


class GalleryAvailable(BaseModel, GalleryBase):
    name: GalleryTypes.name
    parent_id: GalleryTypes.parent_id | None = None
    date: GalleryTypes.date | None = None

    class Config:
        from_attributes = True


class GalleryPublic(BaseModel, GalleryBase):

    id: GalleryTypes.id

    class Config:
        from_attributes = True


class GalleryPrivate(BaseModel, GalleryBase):

    id: GalleryTypes.id
    name: GalleryTypes.name
    parent_id: GalleryTypes.parent_id | None
    description: GalleryTypes.description | None
    datetime: GalleryTypes.date | None

    class Config:
        from_attributes = True


class Gallery(SQLModel, Table[GalleryTypes.id], GalleryBase, table=True):
    __tablename__ = 'gallery'
    id: GalleryTypes.id = Field(
        primary_key=True, index=True)
    name: GalleryTypes.name
    visibility: GalleryTypes.visibility = Field(VisibilityLevel.PUBLIC)
    parent_id: GalleryTypes.parent_id | None = Field(
        default=None, foreign_key=__tablename__ + '.id')
    description: GalleryTypes.name = Field(default='')
    date: GalleryTypes.date | None = Field(default=None)

    @classmethod
    async def is_available(cls, session: Session, gallery_available: GalleryAvailable) -> bool:

        query = select(Gallery).where(
            and_(
                Gallery.name == gallery_available.name,
                Gallery.parent_id == gallery_available.parent_id,
                Gallery.date == gallery_available.date
            )
        )
        return session.exec(query).first() is None


class GalleryCreate(SingularCreate[Gallery], GalleryBase):
    name: GalleryTypes.name
    visibility: typing.Optional[GalleryTypes.visibility] = VisibilityLevel.PUBLIC
    parent_id: typing.Optional[GalleryTypes.parent_id] = None
    description: typing.Optional[GalleryTypes.description] = ''
    date: typing.Optional[GalleryTypes.date] = None

    _SINGULAR_MODEL: typing.ClassVar[typing.Type[Gallery]] = Gallery


class GalleryPermission(SQLModel, Table[typing.Annotated[tuple[str, str], '(gallery_id, user_id)']], table=True):

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
