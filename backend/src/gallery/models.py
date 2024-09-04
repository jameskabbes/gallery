import typing
import uuid
from sqlmodel import SQLModel, Field, Column, Session, select, delete, Relationship
from pydantic import BaseModel, EmailStr, constr, StringConstraints
from gallery import utils
from abc import ABC, abstractmethod
import datetime as datetime_module


class Singular[IDType](ABC):
    _ID_COL: typing.ClassVar[str] = 'id'

    @property
    def _id(self) -> IDType:
        return getattr(self, self._ID_COL)

    @classmethod
    def get_by_id(cls, session: Session, id: IDType) -> typing.Self | None:
        return cls.get_by_key_value(session, cls._ID_COL, id)

    @classmethod
    def get_by_key_value(cls, session: Session, key: str, value: typing.Any) -> typing.Self | None:
        return session.exec(select(cls).where(getattr(cls, key) == value)).first()

    @classmethod
    def key_value_exists(cls, session: Session, key: str, value: typing.Any) -> bool:
        return cls.get_by_key_value(session, key, value) is not None

    def add_to_db(self, session: Session):
        session.add(self)
        session.commit()
        session.refresh(self)

    @classmethod
    def delete_by_id(cls, session: Session, id: IDType) -> bool:
        result = session.exec(delete(cls).where(cls._ID_COL == id))
        session.commit()
        return bool(result)

    def delete(cls, session: Session) -> bool:
        return cls.delete_by_id(session, cls._id)

    @classmethod
    def not_found_message(cls) -> str:
        return f'{cls.__name__} not found'


class SingularCreate(ABC):

    @classmethod
    def generate_id(cls):
        return str(uuid.uuid4())


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'


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


class UserBase:
    _payload_claim: typing.ClassVar[str] = 'sub'

    def export_for_token_payload(self) -> dict:
        return {self._payload_claim: self.id}

    @classmethod
    def import_from_token_payload(self, token_payload: dict) -> UserTypes.id | None:
        return token_payload.get(self._payload_claim)


class User(SQLModel, Singular, UserBase, table=True):
    __tablename__ = 'user'
    id: UserTypes.id = Field(
        primary_key=True, index=True)
    username: UserTypes.username = Field(index=True)
    email: UserTypes.email = Field(index=True)
    hashed_password: UserTypes.hashed_password | None

    collections: list['Collection'] = Relationship(back_populates='user')

    @classmethod
    def authenticate(cls, session: Session, username: str, password: str) -> typing.Self | None:
        user = session.exec(select(cls).where(
            cls.username == username)).first()

        if not user:
            return None
        if not utils.verify_password(password, user.hashed_password):
            return None
        return user


class UserCreate(BaseModel, SingularCreate, UserBase):
    username: UserTypes.username
    email: UserTypes.email
    password: UserTypes.password

    def create(self) -> User:
        return User(
            id=self.generate_id(),
            username=self.username,
            email=self.email,
            hashed_password=utils.hash_password(self.password))


class UserUpdate(BaseModel, UserBase):
    username: typing.Optional[UserTypes.username] = None
    email: typing.Optional[UserTypes.email] = None
    password: typing.Optional[UserTypes.password] = None


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


class CollectionTypes:
    id = str
    name = typing.Annotated[str, StringConstraints(
        min_length=1, max_length=256)]
    user_id = UserTypes.id
    parent_id = typing.Optional[str]  # CollectionTypes.id
    description = typing.Optional[str]
    datetime = typing.Optional[datetime_module.datetime]


class CollectionBase:
    pass


class Collection(SQLModel, Singular, CollectionBase, table=True):
    __tablename__ = 'collection'
    id: CollectionTypes.id = Field(
        primary_key=True, index=True)
    name: CollectionTypes.name
    user_id: CollectionTypes.user_id = Field(
        index=True, foreign_key=User.__tablename__ + '.id')
    parent_id: CollectionTypes.parent_id = Field(
        default=None, foreign_key=__tablename__ + '.id')
    description: CollectionTypes.description = Field(default=None)
    datetime: CollectionTypes.datetime = Field(default=None)

    user: User = Relationship(back_populates='collections')


class CollectionCreate(BaseModel, SingularCreate, CollectionBase):
    pass


class CollectionUpdate(BaseModel, CollectionBase):
    pass


class CollectionPublic(BaseModel, CollectionBase):

    class Config:
        from_attributes = True


class CollectionPrivate(BaseModel, CollectionBase):

    class Config:
        from_attributes = True
