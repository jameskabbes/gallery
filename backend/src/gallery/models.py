import typing
import uuid
from fastapi import HTTPException, status
from sqlmodel import SQLModel, Field, Column, Session, select, delete, Relationship
from pydantic import BaseModel, EmailStr, constr, StringConstraints, field_validator
from sqlalchemy import PrimaryKeyConstraint, and_, or_
from gallery import utils, auth
from abc import ABC, abstractmethod
import datetime as datetime_module
from enum import Enum
import jwt
import pydantic
import collections.abc
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


class Table[IDType]:

    _ID_COLS: typing.ClassVar[list[str]] = ['id']
    type PluralDict = dict[IDType, typing.Self]

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

    @classmethod
    async def get(cls, session: Session, id: IDType) -> typing.Self:
        instance = cls.get_one_by_id(session, id)
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=cls.not_found_message())
        return instance

    @classmethod
    async def delete(cls, session: Session, id: IDType) -> bool:
        if cls.delete_one_by_id(session, id) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=cls.not_found_message())
        else:
            return True

    @classmethod
    def export_plural_to_dict(cls, items: collections.abc.Iterable[typing.Self]) -> PluralDict:
        return {item._id: item for item in items}


class SingularCreate[TableType: Table](BaseModel):
    _SINGULAR_MODEL: typing.ClassVar[typing.Type[TableType]]

    def create(self) -> TableType:
        return self._SINGULAR_MODEL(
            **self.model_dump(),
            id=self._SINGULAR_MODEL.generate_id()
        )


# UserRole
class UserRoleTypes:
    id = str
    name = str


class UserRole(SQLModel, Table[UserRoleTypes.id], table=True):
    __tablename__ = 'user_role'
    id: UserRoleTypes.id = Field(
        primary_key=True, index=True, unique=True, const=True)
    name: UserRoleTypes.name = Field(unique=True)
    users: list['User'] = Relationship(back_populates='user_role')
    user_role_scopes: list['UserRoleScope'] = Relationship(
        back_populates='user_role')


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
    user_role_id = UserRoleTypes.id


class UserBase:
    pass


class UserUpdate(BaseModel, UserBase):
    email: typing.Optional[UserTypes.email] = None
    password: typing.Optional[UserTypes.password] = None
    username: typing.Optional[UserTypes.username] = None


class UserUpdateAdmin(UserUpdate):
    user_role_id: typing.Optional[UserTypes.user_role_id] = None


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
    id: UserTypes.id = Field(
        primary_key=True, index=True, unique=True, const=True)
    email: UserTypes.email = Field(index=True, unique=True)
    username: UserTypes.username = Field(
        index=True, unique=True, nullable=True, default=None)
    hashed_password: UserTypes.hashed_password | None = Field(default=None)
    user_role_id: UserTypes.user_role_id = Field(
        foreign_key=UserRole.__tablename__ + '.id', default='2')

    api_keys: list['APIKey'] = Relationship(back_populates='user')
    user_role: UserRole = Relationship(back_populates='users')
    user_access_tokens: list['UserAccessToken'] = Relationship(
        back_populates='user')

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

    @property
    def is_public(self) -> bool:
        return self.username is not None

    @classmethod
    def patch(cls, session: Session, user_id: UserTypes.id, user_update: UserUpdateAdmin) -> typing.Self:

        user = cls.get_one_by_id(session, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=cls.not_found_message())

        # if they changed their username, check if it's available
        if user_update.username != None:
            if user.username != user_update.username:
                if not cls.is_username_available(session, user_update.username):
                    raise HTTPException(status.HTTP_409_CONFLICT,
                                        detail='Username already exists')

        # if they changed their email, check if it's available
        if user_update.email != None:
            if user.email != user_update.email:
                if not cls.is_email_available(session, user_update.email):
                    raise HTTPException(status.HTTP_409_CONFLICT,
                                        detail='Email already exists')

        exported = user_update.model_dump(
            exclude='password', exclude_unset=True)

        if user_update.password != None:
            exported['hashed_password'] = utils.hash_password(
                user_update.password)

        user.sqlmodel_update(exported)
        user.add_to_db(session)
        return user


class UserCreate(SingularCreate[User], UserBase):
    email: UserTypes.email
    password: typing.Optional[UserTypes.password] = None

    _SINGULAR_MODEL: typing.ClassVar[typing.Type[User]] = User

    def post(self, session: Session) -> User:
        if not User.is_email_available(session, self.email):
            raise HTTPException(status.HTTP_409_CONFLICT,
                                detail='Email already exists')
        user = self.create()
        user.add_to_db(session)
        return user

    def create(self) -> User:

        hashed_password = None
        if self.password:
            hashed_password = utils.hash_password(self.password)

        return User(id=self._SINGULAR_MODEL.generate_id(), email=self.email, hashed_password=hashed_password)


# Scope
type ScopeName = typing.Literal[
    'admin',
    'users.read',
    'users.write'
]


class ScopeNames:
    ADMIN: ScopeName = 'admin'
    USERS_READ: ScopeName = 'users.read'
    USERS_WRITE: ScopeName = 'users.write'


class ScopeTypes:
    id = str
    name = ScopeName


class Scope(SQLModel, Table[ScopeTypes.id], table=True):
    __tablename__ = 'scope'
    id: ScopeTypes.id = Field(
        primary_key=True, index=True, unique=True, const=True)
    name: str = Field(index=True, unique=True)
    user_role_scopes: list['UserRoleScope'] = Relationship(
        back_populates='scope')
    api_key_scopes: list['APIKeyScope'] = Relationship(
        back_populates='scope')

    @classmethod
    def generate_id(cls):
        return len(cls.get_all_by_key_values(cls, {})) + 1


# UserRoleScopes


class UserRoleScopeTypes:
    user_role_id = UserRoleTypes.id
    scope_id = ScopeTypes.id


type UserRoleScopeId = typing.Annotated[tuple[UserRoleScopeTypes.user_role_id,
                                              UserRoleScopeTypes.scope_id], '(user_role_id, scope_id)']


class UserRoleScope(SQLModel, Table[UserRoleScopeId], table=True):
    __tablename__ = 'user_role_scope'
    __table_args__ = (
        PrimaryKeyConstraint('user_role_id', 'scope_id'),
    )
    _ID_COLS: typing.ClassVar[list[str]] = ['user_role_id', 'scope_id']
    user_role_id: UserRoleTypes.id = Field(
        primary_key=True, index=True, foreign_key=UserRole.__tablename__ + '.id')
    scope_id: ScopeTypes.id = Field(
        primary_key=True, index=True, foreign_key=Scope.__tablename__ + '.id')

    user_role: UserRole = Relationship(back_populates='user_role_scopes')
    scope: Scope = Relationship(back_populates='user_role_scopes')

# Auth Credential


class AuthCredentialTypes:
    user_id = UserTypes.id
    issued = typing.Annotated[datetime_module.datetime,
                              'The datetime at which the token was issued']
    expiry = typing.Annotated[datetime_module.datetime,
                              'The datetime at which the token will expire']
    lifespan = typing.Annotated[datetime_module.timedelta,
                                'The timedelta from token creation in which the token is still valid']
    type = typing.Literal['access_token', 'api_key']


class AuthCredential[IDType](BaseModel, ABC):
    user_id: UserTypes.id = Field(
        index=True, foreign_key=User.__tablename__ + '.id', const=True)
    issued: datetime_module.datetime = Field(const=True)
    expiry: AuthCredentialTypes.expiry = Field()
    type: typing.ClassVar[AuthCredentialTypes.type | None] = None

    class JWTExport(typing.TypedDict):
        sub: IDType
        exp: AuthCredentialTypes.expiry
        iat: AuthCredentialTypes.issued
        type: AuthCredentialTypes.type

    _JWT_CLAIMS_TO_ATTRIBUTES: typing.ClassVar[dict[str, str]] = {
        'sub': 'id',
        'exp': 'expiry',
        'iat': 'issued',
        'type': 'type',
    }

    class JWTImport(typing.TypedDict):
        id: IDType
        expiry: AuthCredentialTypes.expiry
        issued: AuthCredentialTypes.issued
        type: AuthCredentialTypes.type

    class ValidateJWTReturn(typing.TypedDict):
        valid: bool
        exception: typing.Optional[auth.EXCEPTION]

    @classmethod
    def validate_jwt_claims(cls, payload: JWTExport) -> bool:
        return all(claim in payload for claim in cls._JWT_CLAIMS_TO_ATTRIBUTES)

    @classmethod
    def import_from_jwt(cls, payload: dict) -> JWTImport:
        return {cls._JWT_CLAIMS_TO_ATTRIBUTES[claim]: payload.get(claim) for claim in cls._JWT_CLAIMS_TO_ATTRIBUTES}

    def export_to_jwt(self) -> JWTExport:
        return {key: getattr(self, value) for key, value in self._JWT_CLAIMS_TO_ATTRIBUTES.items()}

    @abstractmethod
    def get_scopes(self) -> list[Scope]:
        pass


class AuthCredentialCreate(SingularCreate[AuthCredential]):
    user_id: AuthCredentialTypes.user_id
    lifespan: typing.Annotated[datetime_module.timedelta | None,
                               'The timedelta from token creation in which the token is still valid'] = None
    expiry: typing.Annotated[datetime_module.datetime | None,
                             'The datetime at which the token will expire'] = None

    _SINGULAR_MODEL: typing.ClassVar[typing.Type[AuthCredential]
                                     ] = AuthCredential

    @pydantic.model_validator(mode='after')
    def check_lifespan_or_expiry(self):
        if self.lifespan == None and self.expiry == None:
            raise ValueError(
                "Either 'lifespan' or 'expiry' must be set and not None.")
        return self

    def get_expiry(self) -> datetime_module.datetime:

        if self.expiry != None:
            return self.expiry

        return datetime_module.datetime.now(
            datetime_module.UTC) + self.lifespan


class UserAccessTokenTypes(AuthCredentialTypes):
    id = str


class UserAccessToken(SQLModel, AuthCredential[UserAccessTokenTypes.id], Table[UserAccessTokenTypes.id], table=True):
    __tablename__ = 'user_access_token'
    id: UserAccessTokenTypes.id = Field(
        primary_key=True, index=True, unique=True, const=True)
    type: typing.ClassVar[AuthCredentialTypes.type] = 'access_token'

    user: User = Relationship(back_populates='user_access_tokens')

    def get_scopes(self) -> list[Scope]:
        return [user_role_scope.scope for user_role_scope in self.user.user_role.user_role_scopes]


class UserAccessTokenCreate(SingularCreate[UserAccessToken], AuthCredentialCreate):
    _SINGULAR_MODEL: typing.ClassVar[typing.Type[UserAccessToken]
                                     ] = UserAccessToken

    def create(self) -> UserAccessToken:
        return UserAccessToken(
            id=self._SINGULAR_MODEL.generate_id(),
            issued=datetime_module.datetime.now(
                datetime_module.timezone.utc),
            expiry=self.get_expiry(),
            **self.model_dump(exclude=['lifespan', 'expiry'])
        )


# APIKey


class APIKeyTypes(AuthCredentialTypes):
    id = str
    name = str


class APIKeyUpdate(BaseModel):
    name: typing.Optional[APIKeyTypes.name] = None


class APIKey(SQLModel, AuthCredential[APIKeyTypes.id], Table[APIKeyTypes.id], table=True):
    __tablename__ = 'api_key'
    id: APIKeyTypes.id = Field(
        primary_key=True, index=True, unique=True, const=True)
    name: APIKeyTypes.name = Field()
    type: typing.ClassVar[AuthCredentialTypes.type] = 'api_key'

    user: User = Relationship(back_populates='api_keys')
    api_key_scopes: list['APIKeyScope'] = Relationship(
        back_populates='api_key')

    def get_scopes(self) -> list[Scope]:
        return [api_key_scope.scope for api_key_scope in self.api_key_scopes]


class APIKeyCreate(SingularCreate[APIKey], AuthCredentialCreate):
    _SINGULAR_MODEL: typing.ClassVar[typing.Type[UserAccessToken]
                                     ] = UserAccessToken
    name: APIKeyTypes.name

    def create(self) -> APIKey:
        return APIKey(
            id=self._SINGULAR_MODEL.generate_id(),
            issued=datetime_module.datetime.now(
                datetime_module.timezone.utc),
            expiry=self.get_expiry(),
            **self.model_dump(exclude=['lifespan', 'expiry'])
        )


type AuthCredentialClasses = typing.Union[UserAccessToken, APIKey]

# APIKeyScope


class APIKeyScopeTypes:
    api_key_id = APIKeyTypes.id
    scope_id = ScopeTypes.id


type APIKeyScopeID = typing.Annotated[tuple[APIKeyScopeTypes.api_key_id,
                                            APIKeyScopeTypes.scope_id], '(api_key_id, scope_id)'
                                      ]


class APIKeyScope(SQLModel, Table[APIKeyScopeID], table=True):
    __tablename__ = 'api_key_scope'
    __table_args__ = (
        PrimaryKeyConstraint('api_key_id', 'scope_id'),
    )
    _ID_COLS: typing.ClassVar[list[str]] = ['api_key_id', 'scope_id']

    api_key_id: APIKeyScopeTypes.api_key_id = Field(
        index=True, foreign_key=APIKey.__tablename__ + '.id')
    scope_id: APIKeyScopeTypes.scope_id = Field(
        index=True, foreign_key=Scope.__tablename__ + '.id')

    api_key: APIKey = Relationship(back_populates='api_key_scopes')
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
