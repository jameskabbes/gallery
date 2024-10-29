from pydantic import BaseModel, field_validator
import typing
import uuid
from fastapi import HTTPException, status
from sqlmodel import SQLModel, Field, Column, Session, select, delete, Relationship
from pydantic import BaseModel, EmailStr, constr, StringConstraints, field_validator, ValidationInfo, ValidatorFunctionWrapHandler, ValidationError, field_serializer, model_validator
from pydantic.functional_validators import WrapValidator
from sqlalchemy import PrimaryKeyConstraint, and_, or_
from sqlalchemy.types import DateTime
from gallery import utils, auth
from abc import ABC, abstractmethod
import datetime as datetime_module
from enum import Enum
import jwt
import pydantic
import collections.abc
import re
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


def validate_and_normalize_datetime(value: datetime_module.datetime, info: ValidationInfo) -> datetime_module.datetime:
    if value.tzinfo == None:
        raise ValueError(info.field_name + ' must have a timezone')
    return value.astimezone(datetime_module.timezone.utc)


class IDObject[IDType]:

    _ID_COLS: typing.ClassVar[list[str]] = ['id']

    @ property
    def _id(self) -> IDType:
        """Return the ID of the model"""

        if len(self._ID_COLS) > 1:
            return tuple(getattr(self, key) for key in self._ID_COLS)
        else:
            return getattr(self, self._ID_COLS[0])

    @ classmethod
    def export_plural_to_dict(cls, items: collections.abc.Iterable[typing.Self]) -> dict[IDType, typing.Self]:
        return {item._id: item for item in items}


class Table[IDType](SQLModel, IDObject[IDType]):

    @ classmethod
    def generate_id(cls) -> IDType:
        """Generate a new ID for the model"""
        if len(cls._ID_COLS) > 1:
            return tuple(str(uuid.uuid4()) for _ in range(len(cls._ID_COLS)))
        else:
            return str(uuid.uuid4())

    @ classmethod
    def not_found_message(cls) -> str:
        return f'{cls.__name__} not found'

    @ classmethod
    async def get_one_by_id(cls, session: Session, id: IDType) -> typing.Self | None:
        """Get a model by its ID"""

        if len(cls._ID_COLS) > 1:
            assert isinstance(id, (tuple, list))
            assert len(id) == len(cls._ID_COLS)
            resp = await cls._get_by_key_values(session, {cls._ID_COLS[i]: id[i] for i in range(len(cls._ID_COLS))})
        else:
            resp = await cls._get_by_key_values(session, {cls._ID_COLS[0]: id})

        return resp.one_or_none()

    @ classmethod
    async def get_one_by_key_values(cls, session: Session, key_values: dict[str, typing.Any]) -> typing.Self | None:
        """Get a model by its key values"""

        resp = await cls._get_by_key_values(session, key_values)
        return resp.one_or_none()

    @ classmethod
    async def get_all_by_key_values(cls, session: Session, key_values: dict[str, typing.Any]) -> list[typing.Self]:
        """Get all models by their key values"""

        resp = await cls._get_by_key_values(session, key_values)
        return resp.all()

    @ classmethod
    async def _get_by_key_values(cls, session: Session, key_values: dict[str, typing.Any]):

        conditions = [getattr(cls, key) == value for key,
                      value in key_values.items()]

        query = select(cls).where(and_(*conditions))
        return session.exec(query)

    async def add_to_db(self, session: Session):
        """Add the model to the database"""

        session.add(self)
        session.commit()
        session.refresh(self)

    @ classmethod
    async def delete_one_by_id(cls, session: Session, id: IDType) -> int:
        """Delete a model by its ID"""

        return await cls.delete_many_by_ids(session, [id])

    @ classmethod
    async def delete_many_by_ids(cls, session: Session, ids: list[IDType]) -> int:
        """Delete models by their IDs"""

        if len(cls._ID_COLS) > 1:
            conditions = [and_(*[getattr(cls, cls._ID_COLS[i]) == id[i]
                               for i in range(len(cls._ID_COLS))]) for id in ids]
        else:
            conditions = [getattr(cls, cls._ID_COLS[0]) == id for id in ids]

        result = session.exec(delete(cls).where(or_(*conditions)))
        session.commit()
        return result.rowcount

    @ classmethod
    async def is_available(cls, session: Session) -> bool:
        return True

    @ classmethod
    async def get(cls, session: Session, id: IDType) -> typing.Self:
        instance = await cls.get_one_by_id(session, id)
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=cls.not_found_message())
        return instance

    @ classmethod
    async def delete(cls, session: Session, id: IDType) -> bool:
        if await cls.delete_one_by_id(session, id) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=cls.not_found_message())
        else:
            return True


class TableExport[TTable: Table](BaseModel):
    _TABLE_MODEL: typing.ClassVar[typing.Type[TTable]]

    class Config:
        from_attributes = True


class TableImport[TTable: Table](BaseModel):
    _TABLE_MODEL: typing.ClassVar[typing.Type[TTable]] = Table


class TableUpdateAdmin[TTable: Table, IDType](TableImport[TTable], IDObject[IDType]):
    _TABLE_MODEL: typing.ClassVar[typing.Type[TTable]] = Table

    async def patch(self, session: Session) -> TTable:
        table_inst = await self._TABLE_MODEL.get_one_by_id(session, self.id)
        if not table_inst:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=self._TABLE_MODEL.not_found_message())
        table_inst.sqlmodel_update(self.model_dump(exclude_unset=True))
        await table_inst.add_to_db(session)
        return table_inst


class TableCreateAdmin[TTable: Table](TableImport[TTable]):
    _TABLE_MODEL: typing.ClassVar[typing.Type[TTable]] = Table

    async def post(self, session: Session) -> TTable:
        table_inst = await self.create()
        await table_inst.add_to_db(session)
        return table_inst

    async def create(self) -> TTable:
        return self._TABLE_MODEL(
            **{key: value for key, value in zip(self._TABLE_MODEL._ID_COLS, self._TABLE_MODEL.generate_id())}
            ** self.model_dump(),
        )

#
# UserRole
#


class UserRoles:
    ADMIN = 'admin'
    USER = 'user'


USER_ROLE_MAPPING = {
    UserRoles.ADMIN: '1',
    UserRoles.USER: '2'
}


class UserRoleTypes:
    id = str
    name = typing.Annotated[str, StringConstraints(
        min_length=1, to_lower=True)]


class UserRoleIDBase(IDObject[UserRoleTypes.id]):
    id: UserRoleTypes.id = Field(
        primary_key=True, index=True, unique=True, const=True)


class UserRole(Table[UserRoleTypes.id], UserRoleIDBase, table=True):
    __tablename__ = 'user_role'
    name: UserRoleTypes.name = Field(unique=True)

    users: list['User'] = Relationship(back_populates='user_role')
    user_role_scopes: list['UserRoleScope'] = Relationship(
        back_populates='user_role')


type PluralUserRolesDict = dict[UserRoleTypes.id, UserRole]


class UserRoleExport(TableExport[UserRole]):
    _TABLE_MODEL: typing.ClassVar[typing.Type[UserRole]] = UserRole
    id: UserRoleTypes.id
    name: UserRoleTypes.name


class UserRolePublic(UserRoleExport):
    pass


class UserRolePrivate(UserRoleExport):
    pass


class UserRoleImport(TableImport[UserRole]):
    _TABLE_MODEL: typing.ClassVar[typing.Type[UserRole]] = UserRole


class UserRoleUpdate(UserRoleImport, UserRoleIDBase):
    name: typing.Optional[UserRoleTypes.name]


class UserRoleUpdateAdmin(UserRoleUpdate, TableUpdateAdmin[UserRole, UserRoleTypes.id]):
    pass


class UserRoleCreate(UserRoleImport):
    name: UserRoleTypes.name


class UserRoleCreateAdmin(UserRoleCreate, TableCreateAdmin[UserRole]):
    pass


#
# User
#


class UserTypes:
    id = str
    email = typing.Annotated[EmailStr, StringConstraints(
        min_length=1, max_length=254)]
    password = typing.Annotated[str, StringConstraints(
        min_length=1, max_length=64)]
    username = typing.Annotated[str, StringConstraints(
        min_length=3, max_length=20, pattern=re.compile(r'^[a-zA-Z0-9_.-]+$'), to_lower=True)]
    hashed_password = str
    user_role_id = UserRoleTypes.id


class UserIDBase(IDObject[UserTypes.id]):
    id: UserTypes.id = Field(
        primary_key=True, index=True, unique=True, const=True)


class User(Table[UserTypes.id], UserIDBase, table=True):
    __tablename__ = 'user'

    email: UserTypes.email = Field(index=True, unique=True)
    username: UserTypes.username = Field(
        index=True, unique=True, nullable=True, default=None)
    hashed_password: UserTypes.hashed_password | None = Field(default=None)
    user_role_id: UserTypes.user_role_id = Field(
        foreign_key=UserRole.__tablename__ + '.' + UserRole._ID_COLS[0])

    user_role: UserRole = Relationship(back_populates='users')
    api_keys: list['APIKey'] = Relationship(back_populates='user')
    user_access_tokens: list['UserAccessToken'] = Relationship(
        back_populates='user')

    @ property
    def is_public(self) -> bool:
        return self.username is not None

    @ classmethod
    async def authenticate(cls, session: Session, username_or_email: UserTypes.email | UserTypes.username, password: UserTypes.password) -> typing.Self | None:

        user = await cls.get_one_by_key_values(session, {'email': username_or_email})

        if not user:
            user = await cls.get_one_by_key_values(
                session, {'username': username_or_email})
        if not user:
            return None
        if user.hashed_password is None:
            return None
        if not utils.verify_password(password, user.hashed_password):
            return None
        return user

    @ classmethod
    async def is_username_available(cls, session: Session, username: UserTypes.username) -> bool:
        if await cls.get_one_by_key_values(session, {'username': username}):
            return False
        return True

    @ classmethod
    async def is_email_available(cls, session: Session, email: UserTypes.email) -> bool:
        if await cls.get_one_by_key_values(session, {'email': email}):
            return False
        return True

    async def get_scopes(self) -> list['Scope']:
        return [user_role_scope.scope for user_role_scope in self.user_role.user_role_scopes]


type PluralUsersDict = dict[UserTypes.id, User]

# Export Types


class UserExport(TableExport[User]):
    _TABLE_MODEL: typing.ClassVar[typing.Type[User]] = User

    id: UserTypes.id
    username: UserTypes.username | None


class UserPublic(UserExport):
    pass


class UserPrivate(UserExport):
    email: UserTypes.email


# Import Types
class UserImport(TableImport[User]):
    _TABLE_MODEL: typing.ClassVar[typing.Type[User]] = User

    @classmethod
    def hash_password(cls, password: UserTypes.password) -> UserTypes.hashed_password:
        return utils.hash_password(password)


class UserUpdate(UserImport, UserIDBase):
    email: typing.Optional[UserTypes.email] = None
    password: typing.Optional[UserTypes.password] = None
    username: typing.Optional[UserTypes.username] = None


class UserUpdateAdmin(UserUpdate, TableUpdateAdmin[User, UserTypes.id]):
    user_role_id: typing.Optional[UserTypes.user_role_id] = None

    async def patch(self, session: Session) -> User:

        user = await self._TABLE_MODEL.get_one_by_id(session, self.id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=self._TABLE_MODEL.not_found_message())

        # if they changed their username, check if it's available
        if self.username != None:
            if user.username != self.username:
                if not await self._TABLE_MODEL.is_username_available(session, self.username):
                    raise HTTPException(status.HTTP_409_CONFLICT,
                                        detail='Username already exists')

        # if they changed their email, check if it's available
        if self.email != None:
            if user.email != self.email:
                if not await self._TABLE_MODEL.is_email_available(session, self.email):
                    raise HTTPException(status.HTTP_409_CONFLICT,
                                        detail='Email already exists')

        exported = self.model_dump(
            exclude='password', exclude_unset=True)

        if self.password != None:
            exported['hashed_password'] = self.hash_password(self.password)

        # need to do something with the user_role_id
        # if the user role id is changed, also need to remove the scopes from API Keys or other auth credentials with outdated info

        user.sqlmodel_update(exported)
        user.add_to_db(session)
        return user


class UserCreate(UserImport):
    email: UserTypes.email
    password: typing.Optional[UserTypes.password] = None


class UserCreateAdmin(UserCreate, TableCreateAdmin[User]):
    user_role_id: UserTypes.user_role_id = Field(
        default=USER_ROLE_MAPPING[UserRoles.USER])

    async def post(self, session: Session) -> User:
        if not await self._TABLE_MODEL.is_email_available(session, self.email):
            raise HTTPException(status.HTTP_409_CONFLICT,
                                detail='Email already exists')
        user = await self.create()
        await user.add_to_db(session)
        return user

    async def create(self) -> User:

        return self._TABLE_MODEL(
            id=self._TABLE_MODEL.generate_id(),
            hashed_password=None if self.password == None else utils.hash_password(
                self.password),
            **self.model_dump(exclude=['password'])
        )


#
# Scope
#


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


class ScopeIDBase(IDObject[ScopeTypes.id]):
    id: ScopeTypes.id = Field(
        primary_key=True, index=True, unique=True, const=True)


class Scope(Table[ScopeTypes.id], ScopeIDBase, table=True):
    __tablename__ = 'scope'

    name: str = Field(unique=True)

    user_role_scopes: list['UserRoleScope'] = Relationship(
        back_populates='scope')
    api_key_scopes: list['APIKeyScope'] = Relationship(
        back_populates='scope')


type PluralScopesDict = dict[ScopeTypes.id, Scope]


class ScopeExport(TableExport[Scope]):
    _TABLE_MODEL: typing.ClassVar[typing.Type[Scope]] = Scope

    id: ScopeTypes.id
    name: ScopeTypes.name


class ScopePublic(ScopeExport):
    pass


class ScopePrivate(ScopeExport):
    pass


class ScopeImport(TableImport[Scope]):
    _TABLE_MODEL: typing.ClassVar[typing.Type[Scope]] = Scope


class ScopeUpdate(ScopeImport, ScopeIDBase):
    name: typing.Optional[ScopeTypes.name] = None


class ScopeUpdateAdmin(ScopeUpdate, TableUpdateAdmin[Scope, ScopeTypes.id]):
    pass


class ScopeCreate(ScopeImport):
    name: ScopeTypes.name


class ScopeCreateAdmin(ScopeCreate, TableCreateAdmin[Scope]):
    _TABLE_MODEL: typing.ClassVar[typing.Type[Scope]] = Scope


#
# UserRoleScope
#

class UserRoleScopeTypes:
    user_role_id = UserRoleTypes.id
    scope_id = ScopeTypes.id


type UserRoleScopeId = typing.Annotated[tuple[UserRoleScopeTypes.user_role_id,
                                              UserRoleScopeTypes.scope_id], '(user_role_id, scope_id)']


class UserRoleScopeIDBase(IDObject[UserRoleScopeId]):
    _ID_COLS: typing.ClassVar[list[str]] = ['user_role_id', 'scope_id']

    user_role_id: UserRoleTypes.id = Field(
        primary_key=True, index=True, foreign_key=UserRole.__tablename__ + '.' + UserRole._ID_COLS[0])
    scope_id: ScopeTypes.id = Field(
        primary_key=True, index=True, foreign_key=Scope.__tablename__ + '.' + Scope._ID_COLS[0])


class UserRoleScope(Table[UserRoleScopeId], UserRoleScopeIDBase, table=True):
    __tablename__ = 'user_role_scope'
    __table_args__ = (
        PrimaryKeyConstraint('user_role_id', 'scope_id'),
    )

    user_role: UserRole = Relationship(back_populates='user_role_scopes')
    scope: Scope = Relationship(back_populates='user_role_scopes')


type PluralUserRoleScopesDict = dict[UserRoleScopeId, UserRoleScope]


class UserRoleScopeExport(TableExport[UserRoleScope], UserRoleScopeIDBase):
    _TABLE_MODEL: typing.ClassVar[typing.Type[UserRoleScope]] = UserRoleScope


class UserRoleScopePublic(UserRoleScopeExport):
    pass


class UserRoleScopePrivate(UserRoleScopeExport):
    pass


class UserRoleScopeImport(TableImport[UserRoleScope]):
    _TABLE_MODEL: typing.ClassVar[typing.Type[UserRoleScope]] = UserRoleScope


class UserRoleScopeUpdate(UserRoleScopeImport, UserRoleScopeIDBase):
    pass


class UserRoleScopeUpdateAdmin(UserRoleScopeUpdate, TableUpdateAdmin[UserRoleScope, UserRoleScopeId]):
    pass


class UserRoleScopeCreate(UserRoleScopeImport):
    pass


class UserRoleScopeCreateAdmin(UserRoleScopeCreate, TableCreateAdmin[UserRoleScope]):
    pass

#
# AuthCredential
#


class AuthCredentialTypes:
    user_id = UserTypes.id
    issued = typing.Annotated[datetime_module.datetime,
                              'The datetime at which the auth credential was issued']
    expiry = typing.Annotated[datetime_module.datetime,
                              'The datetime at which the auth credential will expire']
    lifespan = typing.Annotated[datetime_module.timedelta,
                                'The timedelta from creation in which the auth credential is still valid']
    type = typing.Literal['access_token', 'api_key']


class AuthCredential[IDType](BaseModel, ABC):
    user_id: UserTypes.id = Field(
        index=True, foreign_key=User.__tablename__ + '.' + User._ID_COLS[0], const=True)
    issued: AuthCredentialTypes.issued = Field(const=True)
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

    @ classmethod
    def validate_jwt_claims(cls, payload: JWTExport) -> bool:
        return all(claim in payload for claim in cls._JWT_CLAIMS_TO_ATTRIBUTES)

    @ classmethod
    def import_from_jwt(cls, payload: dict) -> JWTImport:
        return {cls._JWT_CLAIMS_TO_ATTRIBUTES[claim]: payload.get(claim) for claim in cls._JWT_CLAIMS_TO_ATTRIBUTES}

    def export_to_jwt(self) -> JWTExport:
        return {key: getattr(self, value) for key, value in self._JWT_CLAIMS_TO_ATTRIBUTES.items()}

    @field_validator('issued', 'expiry')
    @classmethod
    def validate_datetime(cls, value: datetime_module.datetime, info: ValidationInfo) -> datetime_module.datetime:
        return validate_and_normalize_datetime(value, info)

    @field_serializer('issued', 'expiry')
    def serialize_datetime(value: datetime_module.datetime) -> datetime_module.datetime:
        return value.replace(tzinfo=datetime_module.timezone.utc)

    @abstractmethod
    async def get_scopes(self) -> list['Scope']:
        return []


class AuthCredentialExport[IDType](TableExport[AuthCredential[IDType]]):
    _TABLE_MODEL: typing.ClassVar[typing.Type[AuthCredential]] = AuthCredential

    user_id: UserTypes.id
    issued: AuthCredentialTypes.issued
    expiry: AuthCredentialTypes.expiry


class AuthCredentialImport[IDType](TableImport[AuthCredential[IDType]]):
    lifespan: typing.Optional[AuthCredentialTypes.lifespan] = None
    expiry: typing.Optional[AuthCredentialTypes.expiry] = None

    @ model_validator(mode='after')
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


class AuthCredentialCreateAdmin[TTable: Table, IDType](AuthCredentialImport[IDType], TableCreateAdmin[TTable]):

    user_id: UserTypes.id

    async def create(self) -> TTable:
        return self._TABLE_MODEL(
            id=self._TABLE_MODEL.generate_id(),
            issued=datetime_module.datetime.now(
                datetime_module.timezone.utc),
            expiry=self.get_expiry(),
            **self.model_dump(exclude=['lifespan', 'expiry'])
        )

#
# User Access Token
#


class UserAccessTokenTypes(AuthCredentialTypes):
    id = str


class UserAccessTokenIDBase(IDObject[UserAccessTokenTypes.id]):
    id: UserAccessTokenTypes.id = Field(
        primary_key=True, index=True, unique=True, const=True)


class UserAccessToken(Table[UserAccessTokenTypes.id], UserAccessTokenIDBase, AuthCredential[UserAccessTokenTypes.id], table=True):
    type: typing.ClassVar[AuthCredentialTypes.type] = 'access_token'
    __tablename__ = 'user_access_token'

    user: User = Relationship(back_populates='user_access_tokens')

    async def get_scopes(self) -> list['Scope']:
        return await self.user.get_scopes()


type PluralUserAccessTokensDict = dict[UserAccessTokenTypes.id,
                                       UserAccessToken]


class UserAccessTokenExport(TableExport[UserAccessToken], AuthCredentialExport[UserAccessTokenTypes.id]):
    _TABLE_MODEL: typing.ClassVar[typing.Type[UserAccessToken]
                                  ] = UserAccessToken


class UserAccessTokenPublic(UserAccessTokenExport):
    pass


class UserAccessTokenPrivate(UserAccessTokenExport):
    pass


class UserAccessTokenImport(AuthCredentialImport[UserAccessTokenTypes.id]):
    _TABLE_MODEL: typing.ClassVar[typing.Type[UserAccessToken]
                                  ] = UserAccessToken


class UserAccessTokenUpdate(UserAccessTokenImport, UserAccessTokenIDBase):
    pass


class UserAccessTokenUpdateAdmin(UserAccessTokenUpdate, TableUpdateAdmin[UserAccessToken, UserAccessTokenTypes.id]):
    pass


class UserAccessTokenCreate(UserAccessTokenImport):
    pass


class UserAccessTokenCreateAdmin(UserAccessTokenCreate, AuthCredentialCreateAdmin[UserAccessToken, UserAccessTokenTypes.id]):
    pass

# # APIKey


class APIKeyTypes(AuthCredentialTypes):
    id = str
    name = typing.Annotated[str, StringConstraints(
        min_length=1, max_length=256)]


class APIKeyIDBase(IDObject[APIKeyTypes.id]):
    id: APIKeyTypes.id = Field(
        primary_key=True, index=True, unique=True, const=True)


class APIKey(Table[APIKeyTypes.id], APIKeyIDBase, AuthCredential[APIKeyTypes.id], table=True):
    __tablename__ = 'api_key'

    name: APIKeyTypes.name = Field()
    type: typing.ClassVar[AuthCredentialTypes.type] = 'api_key'

    user: User = Relationship(back_populates='api_keys')
    api_key_scopes: list['APIKeyScope'] = Relationship(
        back_populates='api_key')

    async def get_scopes(self) -> list[Scope]:
        return [api_key_scope.scope for api_key_scope in self.api_key_scopes]


type PluralAPIKeysDict = dict[APIKeyTypes.id, APIKey]


class APIKeyExport(TableExport[APIKey], AuthCredentialExport[APIKeyTypes.id]):
    _TABLE_MODEL: typing.ClassVar[typing.Type[APIKey]] = APIKey
    name: APIKeyTypes.name


class APIKeyPublic(APIKeyExport):
    pass


class APIKeyPrivate(APIKeyExport):
    pass


class APIKeyImport(AuthCredentialImport[APIKeyTypes.id]):
    _TABLE_MODEL: typing.ClassVar[typing.Type[APIKey]] = APIKey


class APIKeyUpdate(APIKeyImport, APIKeyIDBase):
    name: typing.Optional[APIKeyTypes.name] = None


class APIKeyUpdateAdmin(APIKeyUpdate, TableUpdateAdmin[APIKey, APIKeyTypes.id]):
    pass


class APIKeyCreate(APIKeyImport):
    name: APIKeyTypes.name


class APIKeyCreateAdmin(APIKeyCreate, AuthCredentialCreateAdmin[APIKey, APIKeyTypes.id]):
    pass


# AuthCredentialTypes

AUTH_CREDENTIAL_MODEL = typing.Union[UserAccessToken, APIKey]
AUTH_CREDENTIAL_MODEL_MAPPING: dict[AuthCredentialTypes.type, AUTH_CREDENTIAL_MODEL] = {
    'access_token': UserAccessToken,
    'api_key': APIKey
}


#
# APIKeyScope
#

class APIKeyScopeTypes:
    api_key_id = APIKeyTypes.id
    scope_id = ScopeTypes.id


type APIKeyScopeID = typing.Annotated[tuple[APIKeyScopeTypes.api_key_id,
                                            APIKeyScopeTypes.scope_id], '(api_key_id, scope_id)'
                                      ]


class APIKeyScopeIDBase(IDObject[APIKeyScopeID]):
    api_key_id: APIKeyScopeTypes.api_key_id = Field(
        index=True, foreign_key=APIKey.__tablename__ + '.' + APIKey._ID_COLS[0])
    scope_id: APIKeyScopeTypes.scope_id = Field(
        index=True, foreign_key=Scope.__tablename__ + '.' + Scope._ID_COLS[0])


class APIKeyScope(Table[APIKeyScopeID], APIKeyScopeIDBase, table=True):
    __tablename__ = 'api_key_scope'
    __table_args__ = (
        PrimaryKeyConstraint('api_key_id', 'scope_id'),
    )

    _ID_COLS: typing.ClassVar[list[str]] = ['api_key_id', 'scope_id']

    api_key: APIKey = Relationship(back_populates='api_key_scopes')
    scope: Scope = Relationship(back_populates='api_key_scopes')


type PluralAPIKeyScopesDict = dict[APIKeyScopeID, APIKeyScope]


class APIKeyScopeExport(TableExport[APIKeyScope], APIKeyScopeIDBase):
    _TABLE_MODEL: typing.ClassVar[typing.Type[APIKeyScope]] = APIKeyScope


class APIKeyScopePublic(APIKeyScopeExport):
    pass


class APIKeyScopePrivate(APIKeyScopeExport):
    pass


class APIKeyScopeImport(TableImport[APIKeyScope]):
    _TABLE_MODEL: typing.ClassVar[typing.Type[APIKeyScope]] = APIKeyScope


# # Gallery


# # class GalleryTypes:
# #     id = str
# #     name = typing.Annotated[str, StringConstraints(
# #         min_length=1, max_length=256)]
# #     visibility = VisibilityLevel
# #     parent_id = str  # GalleryTypes.id
# #     description = typing.Annotated[str, StringConstraints(
# #         min_length=1, max_length=20000)]
# #     date = datetime_module.date


# # class GalleryBase:
# #     pass


# # class GalleryUpdate(BaseModel, GalleryBase):
# #     name: typing.Optional[GalleryTypes.name] = None
# #     visibility: typing.Optional[GalleryTypes.visibility] = None
# #     parent_id: typing.Optional[GalleryTypes.parent_id] = None
# #     description: typing.Optional[GalleryTypes.description] = None
# #     date: typing.Optional[GalleryTypes.date] = None


# # class GalleryAvailable(BaseModel, GalleryBase):
# #     name: GalleryTypes.name
# #     parent_id: GalleryTypes.parent_id | None = None
# #     date: GalleryTypes.date | None = None

# #     class Config:
# #         from_attributes = True


# # class GalleryPublic(BaseModel, GalleryBase):

# #     id: GalleryTypes.id

# #     class Config:
# #         from_attributes = True


# # class GalleryPrivate(BaseModel, GalleryBase):

# #     id: GalleryTypes.id
# #     name: GalleryTypes.name
# #     parent_id: GalleryTypes.parent_id | None
# #     description: GalleryTypes.description | None
# #     datetime: GalleryTypes.date | None

# #     class Config:
# #         from_attributes = True


# # class Gallery(SQLModel, Table[GalleryTypes.id], GalleryBase, table=True):
# #     __tablename__ = 'gallery'
# #     id: GalleryTypes.id = Field(
# #         primary_key=True, index=True)
# #     name: GalleryTypes.name
# #     visibility: GalleryTypes.visibility = Field(VisibilityLevel.PUBLIC)
# #     parent_id: GalleryTypes.parent_id | None = Field(
# #         default=None, foreign_key=__tablename__ + '.id')
# #     description: GalleryTypes.name = Field(default='')
# #     date: GalleryTypes.date | None = Field(default=None)

# #     @classmethod
# #     async def is_available(cls, session: Session, gallery_available: GalleryAvailable) -> bool:

# #         query = select(Gallery).where(
# #             and_(
# #                 Gallery.name == gallery_available.name,
# #                 Gallery.parent_id == gallery_available.parent_id,
# #                 Gallery.date == gallery_available.date
# #             )
# #         )
# #         return session.exec(query).first() is None
# # class GalleryCreate(IDObjectCreate[Gallery], GalleryBase):
# #     name: GalleryTypes.name
# #     visibility: typing.Optional[GalleryTypes.visibility] = VisibilityLevel.PUBLIC
# #     parent_id: typing.Optional[GalleryTypes.parent_id] = None
# #     description: typing.Optional[GalleryTypes.description] = ''
# #     date: typing.Optional[GalleryTypes.date] = None
# #     _IDObject_MODEL: typing.ClassVar[typing.Type[Gallery]] = Gallery
# # class GalleryPermission(SQLModel, Table[typing.Annotated[tuple[str, str], '(gallery_id, user_id)']], table=True):
# #     __tablename__ = 'gallery_permission'
# #     __table_args__ = (
# #         PrimaryKeyConstraint('gallery_id', 'user_id'),
# #     )
# #     _ID_COLS: typing.ClassVar[list[str]] = ['gallery_id', 'user_id']
# #     gallery_id: GalleryTypes.id = Field(
# #         primary_key=True, index=True, foreign_key=Gallery.__tablename__ + '.id')
# #     user_id: UserTypes.id = Field(
# #         primary_key=True, index=True, foreign_key=UserTable.__tablename__ + '.id')
# #     permission_level: PermissionLevel
# if __name__ == '__main__':
#     print()
