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


class JWTSerializable:

    _jwt_claim_to_attributes: typing.ClassVar[dict[str, str]] = {}

    def _export_to_jwt_base(self) -> dict:
        return {key: getattr(self, value) for key, value in self._jwt_claim_to_attributes.items()}

    @abstractmethod
    def export_to_jwt(self) -> dict:
        return self._export_to_jwt_base()

    @classmethod
    def _import_from_jwt_base(cls, token_payload: dict) -> dict:
        return {cls._jwt_claim_to_attributes[claim]: token_payload.get(claim) for claim in cls._jwt_claim_to_attributes}

    @classmethod
    @abstractmethod
    def import_from_jwt(cls, token_payload: dict) -> dict:
        return cls._import_from_jwt_base(token_payload)


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


class UserBase(JWTSerializable):

    _jwt_claim_to_attributes: typing.ClassVar[dict[str, str]] = {
        'sub': 'id'
    }

    class JWTExport(typing.TypedDict):
        sub: UserTypes.id

    class JWTImport(typing.TypedDict):
        id: UserTypes.id

    def export_to_jwt(self) -> JWTExport:
        return self._export_to_jwt_base()

    @classmethod
    def import_from_jwt(cls, token_payload: dict) -> JWTImport:
        return cls._import_from_jwt_base(token_payload)


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
    hashed_password: UserTypes.hashed_password | None = Field(default=None)
    scopes: list['UserScope'] = Relationship(back_populates='user')
    api_keys: list['APIKey'] = Relationship(back_populates='user')

    @classmethod
    def authenticate(cls, session: Session, email: UserTypes.email, password: UserTypes.password) -> typing.Self | None:

        user = cls.get_one_by_key_values(session, {'email': email})
        if not user:
            return None
        if user.hashed_password is None:
            return None
        if not utils.verify_password(password, user.hashed_password):
            return None
        return user

    @classmethod
    def is_username_available(cls, session: Session, username: UserTypes.username) -> bool:
        if len(username) < 1:
            return False
        if cls.get_one_by_key_values(session, {'username': username}):
            return False
        return True

    @classmethod
    def is_email_available(cls, session: Session, email: UserTypes.email) -> bool:
        if cls.get_one_by_key_values(session, {'email': email}):
            return False
        return True


class UserCreate(SingularCreate[User], UserBase):
    email: UserTypes.email
    password: UserTypes.password | None = None

    _SINGULAR_MODEL: typing.ClassVar[typing.Type[User]] = User

    def create(self) -> User:

        hashed_password = None
        if self.password:
            hashed_password = utils.hash_password(self.password)

        return User(id=self._SINGULAR_MODEL.generate_id(), email=self.email, hashed_password=hashed_password)


# ApiKeys

class APIKeyTypes:
    id = str
    user_id = UserTypes.id
    scope = str
    issued = datetime_module.datetime
    expiry = datetime_module.datetime


class APIKeyBase(JWTSerializable):
    _jwt_claim_to_attributes: typing.ClassVar[dict[str, str]] = {
        'sub': 'id'
    }

    class JWTExport(typing.TypedDict):
        sub: APIKeyTypes.id

    class JWTImport(typing.TypedDict):
        id: APIKeyTypes.id

    def export_to_jwt(self) -> JWTExport:
        return self._export_to_jwt_base()

    @classmethod
    def import_from_jwt(cls, token_payload: dict) -> JWTImport:
        return cls._import_from_jwt_base(token_payload)


class APIKeyUpdate(BaseModel, APIKeyBase):
    scope: APIKeyTypes.scope | None = None
    expiry: APIKeyTypes.expiry | None = None


class APIKeyPrivate(BaseModel, APIKeyBase):
    id: APIKeyTypes.id
    user_id: APIKeyTypes.user_id
    issued: APIKeyTypes.issued
    expiry: APIKeyTypes.expiry

    class Config:
        from_attributes = True


class APIKey(SQLModel, Table[APIKeyTypes.id], APIKeyBase, table=True):
    __tablename__ = 'api_key'
    id: APIKeyTypes.id = Field(primary_key=True, index=True, unique=True)
    user_id: APIKeyTypes.user_id = Field(
        index=True, foreign_key=User.__tablename__ + '.id')
    expiry: APIKeyTypes.expiry | None = Field(default=None)
    issued: APIKeyTypes.issued = Field(default=datetime_module.datetime.now())
    user: User = Relationship(back_populates="api_keys")
    scopes: list["APIKeyScope"] = Relationship(back_populates="api_key")


class APIKeyCreate(SingularCreate[APIKey], APIKeyBase):
    user_id: APIKeyTypes.user_id
    expiry: APIKeyTypes.expiry | None = None

    _SINGULAR_MODEL: typing.ClassVar[typing.Type[APIKey]] = APIKey

    def create(self) -> APIKey:
        return APIKey(id=self._SINGULAR_MODEL.generate_id(), **self.model_dump())

# Scope


type ScopeID = typing.Literal['users.read', 'users.write']


class ScopeTypes:
    id = str


class Scope(SQLModel, Table[ScopeID], table=True):
    __tablename__ = 'scope'
    id: ScopeTypes.id = Field(primary_key=True, index=True, unique=True)
    user_scopes: list['UserScope'] = Relationship(back_populates='scope')
    api_key_scopes: list['APIKeyScope'] = Relationship(back_populates='scope')

# UserScope


class UserScopeTypes:
    pass


class UserScope(SQLModel, Table[UserTypes.id], table=True):
    __tablename__ = 'user_scope'
    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'scope_id'),
    )
    _ID_COLS: typing.ClassVar[list[str]] = ['user_id', 'scope_id']

    user_id: UserTypes.id = Field(
        primary_key=True, index=True, foreign_key=User.__tablename__ + '.id')
    scope_id: ScopeTypes.id = Field(
        primary_key=True, foreign_key=Scope.__tablename__ + '.id')
    user: User = Relationship(back_populates='scopes')
    scope: Scope = Relationship(back_populates='user_scopes')

# APIKeyScope


class APIKeyScope(SQLModel, table=True):
    __tablename__ = 'api_key_scope'
    api_key_id: APIKeyTypes.id = Field(
        primary_key=True, index=True, foreign_key=APIKey.__tablename__ + '.id')
    scope_id: ScopeTypes.id = Field(
        primary_key=True, index=True, foreign_key=Scope.__tablename__ + '.id')
    api_key: APIKey = Relationship(back_populates='scopes')
    scope: Scope = Relationship(back_populates='api_key_scopes')


# Gallery


# class GalleryTypes:
#     id = str
#     name = typing.Annotated[str, StringConstraints(
#         min_length=1, max_length=256)]
#     visibility = VisibilityLevel
#     parent_id = str  # GalleryTypes.id
#     description = typing.Annotated[str, StringConstraints(
#         min_length=1, max_length=20000)]
#     date = datetime_module.date


# class GalleryBase:
#     pass


# class GalleryUpdate(BaseModel, GalleryBase):
#     name: typing.Optional[GalleryTypes.name] = None
#     visibility: typing.Optional[GalleryTypes.visibility] = None
#     parent_id: typing.Optional[GalleryTypes.parent_id] = None
#     description: typing.Optional[GalleryTypes.description] = None
#     date: typing.Optional[GalleryTypes.date] = None


# class GalleryAvailable(BaseModel, GalleryBase):
#     name: GalleryTypes.name
#     parent_id: GalleryTypes.parent_id | None = None
#     date: GalleryTypes.date | None = None

#     class Config:
#         from_attributes = True


# class GalleryPublic(BaseModel, GalleryBase):

#     id: GalleryTypes.id

#     class Config:
#         from_attributes = True


# class GalleryPrivate(BaseModel, GalleryBase):

#     id: GalleryTypes.id
#     name: GalleryTypes.name
#     parent_id: GalleryTypes.parent_id | None
#     description: GalleryTypes.description | None
#     datetime: GalleryTypes.date | None

#     class Config:
#         from_attributes = True


# class Gallery(SQLModel, Table[GalleryTypes.id], GalleryBase, table=True):
#     __tablename__ = 'gallery'
#     id: GalleryTypes.id = Field(
#         primary_key=True, index=True)
#     name: GalleryTypes.name
#     visibility: GalleryTypes.visibility = Field(VisibilityLevel.PUBLIC)
#     parent_id: GalleryTypes.parent_id | None = Field(
#         default=None, foreign_key=__tablename__ + '.id')
#     description: GalleryTypes.name = Field(default='')
#     date: GalleryTypes.date | None = Field(default=None)

#     @classmethod
#     async def is_available(cls, session: Session, gallery_available: GalleryAvailable) -> bool:

#         query = select(Gallery).where(
#             and_(
#                 Gallery.name == gallery_available.name,
#                 Gallery.parent_id == gallery_available.parent_id,
#                 Gallery.date == gallery_available.date
#             )
#         )
#         return session.exec(query).first() is None


# class GalleryCreate(SingularCreate[Gallery], GalleryBase):
#     name: GalleryTypes.name
#     visibility: typing.Optional[GalleryTypes.visibility] = VisibilityLevel.PUBLIC
#     parent_id: typing.Optional[GalleryTypes.parent_id] = None
#     description: typing.Optional[GalleryTypes.description] = ''
#     date: typing.Optional[GalleryTypes.date] = None

#     _SINGULAR_MODEL: typing.ClassVar[typing.Type[Gallery]] = Gallery


# class GalleryPermission(SQLModel, Table[typing.Annotated[tuple[str, str], '(gallery_id, user_id)']], table=True):

#     __tablename__ = 'gallery_permission'
#     __table_args__ = (
#         PrimaryKeyConstraint('gallery_id', 'user_id'),
#     )
#     _ID_COLS: typing.ClassVar[list[str]] = ['gallery_id', 'user_id']

#     gallery_id: GalleryTypes.id = Field(
#         primary_key=True, index=True, foreign_key=Gallery.__tablename__ + '.id')
#     user_id: UserTypes.id = Field(
#         primary_key=True, index=True, foreign_key=User.__tablename__ + '.id')
#     permission_level: PermissionLevel


if __name__ == '__main__':
    print()
