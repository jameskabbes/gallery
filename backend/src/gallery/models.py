from pydantic import BaseModel, field_validator
import typing
from typing import Unpack
import uuid
from fastapi import HTTPException, status, Response
from sqlmodel import SQLModel, Field, Column, Session, select, delete, Relationship
from pydantic import BaseModel, EmailStr, constr, StringConstraints, field_validator, ValidationInfo, ValidatorFunctionWrapHandler, ValidationError, field_serializer, model_validator, conint
from pydantic.functional_validators import WrapValidator
from sqlalchemy import PrimaryKeyConstraint, and_, or_, event
from sqlalchemy.types import DateTime
from gallery import utils, auth
from abc import ABC, abstractmethod
import datetime as datetime_module
from enum import IntEnum, Enum
import jwt
import pydantic
import collections.abc
import re
import pathlib
from gallery import client
import shutil

#


class ApiMethodBaseKwargs(typing.TypedDict):
    session: Session
    c: client.Client
    authorized_user_id: str | None
    admin: bool


class ApiMethodBaseKwargsWithId[IdType](ApiMethodBaseKwargs):
    id: IdType


class ApiGetMethodKwargs[IdType](ApiMethodBaseKwargsWithId[IdType]):
    pass


class ApiPostMethodKwargs(ApiMethodBaseKwargs):
    pass


class ApiPatchMethodKwargs[IdType](ApiMethodBaseKwargsWithId[IdType]):
    pass


class ApiDeleteMethodKwargs[IdType](ApiMethodBaseKwargsWithId[IdType]):
    pass


def validate_and_normalize_datetime(value: datetime_module.datetime, info: ValidationInfo) -> datetime_module.datetime:
    if value.tzinfo == None:
        raise ValueError(info.field_name + ' must have a timezone')
    return value.astimezone(datetime_module.timezone.utc)


class IdObject[IdType]:

    _ID_COLS: typing.ClassVar[list[str]] = ['id']

    @ property
    def _id(self) -> IdType:
        """Return the ID of the model"""

        if len(self._ID_COLS) > 1:
            return tuple(getattr(self, key) for key in self._ID_COLS)
        else:
            return getattr(self, self._ID_COLS[0])

    @ classmethod
    def export_plural_to_dict(cls, items: collections.abc.Iterable[typing.Self]) -> dict[IdType, typing.Self]:
        return {item._id: item for item in items}


class Table[IdType](SQLModel, IdObject[IdType]):

    @ classmethod
    def generate_id(cls) -> IdType:
        """Generate a new ID for the model"""

        if len(cls._ID_COLS) > 1:
            return tuple(str(uuid.uuid4()) for _ in range(len(cls._ID_COLS)))
        else:
            return str(uuid.uuid4())

    @ classmethod
    def not_found_message(cls) -> str:
        return f'{cls.__name__} not found'

    @classmethod
    def already_exists_message(cls) -> str:
        return f'{cls.__name__} already exists'

    @ classmethod
    async def get_one_by_id(cls, session: Session, id: IdType) -> typing.Self | None:
        """Get a model by its ID"""

        if len(cls._ID_COLS) > 1:
            assert isinstance(id, tuple)
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

    @classmethod
    async def _get_by_key_values(cls, session: Session, key_values: dict[str, typing.Any]):
        conditions = []
        for key, value in key_values.items():
            if isinstance(value, list):
                conditions.append(getattr(cls, key).in_(value))
            else:
                conditions.append(getattr(cls, key) == value)

        query = select(cls).where(and_(*conditions))
        return session.exec(query)

    async def add_to_db(self, session: Session):
        """Add the model to the database"""

        session.add(self)
        session.commit()
        session.refresh(self)

    @ classmethod
    async def delete_one_by_id(cls, session: Session, id: IdType) -> int:
        """Delete a model by its ID"""

        return await cls.delete_many_by_ids(session, [id])

    @ classmethod
    async def delete_many_by_ids(cls, session: Session, ids: list[IdType]) -> int:
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
    async def _basic_api_get(cls, session: Session, id: IdType) -> typing.Self:
        """Get a model by its ID, raise an exception if not found"""

        instance = await cls.get_one_by_id(session, id)
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=cls.not_found_message())
        return instance

    @classmethod
    async def api_get(cls, **kwargs: Unpack[ApiGetMethodKwargs[IdType]]) -> typing.Self:
        return await cls._basic_api_get(kwargs['session'], kwargs['id'])

    @classmethod
    async def api_delete(cls, **kwargs: Unpack[ApiDeleteMethodKwargs[IdType]]) -> None:

        table_inst = await cls._basic_api_get(kwargs['session'], kwargs['id'])
        kwargs['session'].delete(table_inst)
        kwargs['session'].commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)


class TableExport[TTable: Table](BaseModel):
    _TABLE_MODEL: typing.ClassVar[typing.Type[TTable]]

    class Config:
        from_attributes = True


class TableImport[TTable: Table](BaseModel):
    _TABLE_MODEL: typing.ClassVar[typing.Type[TTable]] = Table


class TableUpdateAdmin[TTable: Table, IdType](TableImport[TTable], IdObject[IdType]):
    _TABLE_MODEL: typing.ClassVar[typing.Type[TTable]] = Table

    async def api_patch(self, **kwargs: typing.Unpack[ApiPatchMethodKwargs[IdType]]) -> TTable:
        table_inst = await self._TABLE_MODEL.api_get(**kwargs)
        table_inst.sqlmodel_update(self.model_dump(exclude_unset=True))
        await table_inst.add_to_db(kwargs['session'])
        return table_inst


class TableCreateAdmin[TTable: Table](TableImport[TTable]):
    _TABLE_MODEL: typing.ClassVar[typing.Type[TTable]] = Table

    async def api_post(self, **kwargs: typing.Unpack[ApiPostMethodKwargs]) -> TTable:
        table_inst = await self.create()
        await table_inst.add_to_db(kwargs['session'])
        return table_inst

    async def create(self) -> TTable:

        id = self._TABLE_MODEL.generate_id()
        if len(self._TABLE_MODEL._ID_COLS) == 1:
            id = [id]

        return self._TABLE_MODEL(
            **{key: value for key, value in zip(
                self._TABLE_MODEL._ID_COLS, id)},
            ** self.model_dump(),
        )


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
    user_role_id = client.UserRoleTypes.id


class UserIDBase(IdObject[UserTypes.id]):
    id: UserTypes.id = Field(
        primary_key=True, index=True, unique=True, const=True)


class User(Table[UserTypes.id], UserIDBase, table=True):
    __tablename__ = 'user'

    email: UserTypes.email = Field(index=True, unique=True)
    username: UserTypes.username = Field(
        index=True, unique=True, nullable=True)
    hashed_password: UserTypes.hashed_password | None = Field()
    user_role_id: UserTypes.user_role_id = Field()

    api_keys: list['ApiKey'] = Relationship(
        back_populates='user', cascade_delete=True)
    user_access_tokens: list['UserAccessToken'] = Relationship(
        back_populates='user', cascade_delete=True)
    galleries: list['Gallery'] = Relationship(
        back_populates='user', cascade_delete=True)
    gallery_permissions: list['GalleryPermission'] = Relationship(
        back_populates='user', cascade_delete=True)

    @ property
    def is_public(self) -> bool:
        return self.username is not None

    def get_dir(self, root: pathlib.Path) -> pathlib.Path:
        if self.is_public:
            return root / self.username
        else:
            return root / self.id

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

    @classmethod
    async def api_get_is_username_available(cls, session: Session, username: UserTypes.username) -> None:
        if not await cls.is_username_available(session, username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail='Username already exists')

    @ classmethod
    async def is_email_available(cls, session: Session, email: UserTypes.email) -> bool:
        if await cls.get_one_by_key_values(session, {'email': email}):
            return False
        return True

    @classmethod
    async def api_get_is_email_available(cls, session: Session, email: UserTypes.email) -> None:
        if not await cls.is_email_available(session, email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail='Email already exists')

    @ classmethod
    async def api_get(cls, **kwargs: Unpack[ApiGetMethodKwargs[UserTypes.id]]) -> typing.Self:

        user = await cls._basic_api_get(kwargs['session'], kwargs['id'])
        if not user.is_public:
            if not kwargs['admin']:
                if user.id != kwargs['authorized_user_id']:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail=cls.not_found_message())

        return user

    @classmethod
    async def api_delete(cls, **kwargs: Unpack[ApiDeleteMethodKwargs[UserTypes.id]]) -> None:

        user = await cls._basic_api_get(kwargs['session'], kwargs['id'])

        if not kwargs['admin']:
            if user.id != kwargs['authorized_user_id']:

                # cannot edit the user,
                if user.is_public:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to delete this user')

                # pretend the user doesn't exist
                else:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail=cls.not_found_message())

        # delete the root gallery folder
        root_gallery = await Gallery.get_root_gallery(
            kwargs['session'], kwargs['id'])
        shutil.rmtree((await root_gallery.get_dir(kwargs['session'], kwargs['c'].galleries_dir)))

        kwargs['session'].delete(user)
        kwargs['session'].commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)


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
    user_role_id: UserTypes.user_role_id


# Import Types
class UserImport(TableImport[User]):
    _TABLE_MODEL: typing.ClassVar[typing.Type[User]] = User

    @classmethod
    def hash_password(cls, password: UserTypes.password) -> UserTypes.hashed_password:
        return utils.hash_password(password)


class UserUpdate(UserImport):
    email: typing.Optional[UserTypes.email] = None
    password: typing.Optional[UserTypes.password] = None
    username: typing.Optional[UserTypes.username] = None


class UserUpdateAdmin(UserUpdate, TableUpdateAdmin[User, UserTypes.id]):
    async def api_patch(self, **kwargs: Unpack[ApiPatchMethodKwargs[UserTypes.id]]) -> User:

        user = await self._TABLE_MODEL._basic_api_get(kwargs['session'], kwargs['id'])

        if not kwargs['admin']:
            if user.id != kwargs['authorized_user_id']:
                if user.is_public:
                    raise HTTPException(
                        status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to patch this user')
                else:
                    raise HTTPException(
                        status.HTTP_404_NOT_FOUND, detail=self._TABLE_MODEL.not_found_message())

        if 'username' in self.model_fields_set:
            # username has been changed
            if user.username != self.username:
                root_gallery = await Gallery.get_root_gallery(kwargs['session'], kwargs['id'])

                print(root_gallery)

                if self.username == None:
                    await GalleryUpdateAdmin(name=user.id).api_patch(
                        **{**kwargs, **{'id': root_gallery.id}})

                if self.username is not None:
                    await User.api_get_is_username_available(kwargs['session'], self.username)
                    await GalleryUpdateAdmin(name=self.username).api_patch(
                        **{**kwargs, **{'id': root_gallery.id}})

                user.username = self.username

        if 'email' in self.model_fields_set:
            if user.email != self.email:
                await User.api_get_is_email_available(kwargs['session'], self.email)
                user.email = self.email

        if 'password' in self.model_fields_set:
            if self.password == None:
                user.hashed_password = None
            else:
                user.hashed_password = self.hash_password(self.password)

        await user.add_to_db(kwargs['session'])
        return user


class UserCreate(UserImport):
    email: UserTypes.email
    password: typing.Optional[UserTypes.password] = None


class UserCreateAdmin(UserCreate, TableCreateAdmin[User]):
    user_role_id: UserTypes.user_role_id

    async def api_post(self, **kwargs: Unpack[ApiPostMethodKwargs]) -> User:

        await User.api_get_is_email_available(kwargs['session'], self.email)
        user = await self.create()
        await user.add_to_db(kwargs['session'])

        root_gallery = await GalleryCreateAdmin(name='root', user_id=user.id, visibility_level=kwargs['c'].visibility_level_name_mapping['private']).api_post(**kwargs)
        deleted_gallery = await GalleryCreateAdmin(name='deleted', user_id=user.id, visibility_level=kwargs['c'].visibility_level_name_mapping['private'], parent_id=root_gallery._id).api_post(**kwargs)

        return user

    async def create(self) -> User:

        return self._TABLE_MODEL(
            id=self._TABLE_MODEL.generate_id(),
            hashed_password=None if self.password == None else utils.hash_password(
                self.password),
            **self.model_dump(exclude=['password'])
        )


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


class AuthCredential[IdType](BaseModel, ABC):
    user_id: UserTypes.id = Field(
        index=True, foreign_key=User.__tablename__ + '.' + User._ID_COLS[0], const=True, ondelete='CASCADE')
    issued: AuthCredentialTypes.issued = Field(const=True)
    expiry: AuthCredentialTypes.expiry = Field()

    type: typing.ClassVar[AuthCredentialTypes.type | None] = None

    class JwtExport(typing.TypedDict):
        sub: IdType
        exp: AuthCredentialTypes.expiry
        iat: AuthCredentialTypes.issued
        type: AuthCredentialTypes.type

    _JWT_CLAIMS_TO_ATTRIBUTES: typing.ClassVar[dict[str, str]] = {
        'sub': 'id',
        'exp': 'expiry',
        'iat': 'issued',
        'type': 'type',
    }

    class JwtImport(typing.TypedDict):
        id: IdType
        expiry: AuthCredentialTypes.expiry
        issued: AuthCredentialTypes.issued
        type: AuthCredentialTypes.type

    class ValidateJWTReturn(typing.TypedDict):
        valid: bool
        exception: typing.Optional[auth.EXCEPTION]

    @ classmethod
    def validate_jwt_claims(cls, payload: JwtExport) -> bool:
        return all(claim in payload for claim in cls._JWT_CLAIMS_TO_ATTRIBUTES)

    @ classmethod
    def import_from_jwt(cls, payload: dict) -> JwtImport:
        return {cls._JWT_CLAIMS_TO_ATTRIBUTES[claim]: payload.get(claim) for claim in cls._JWT_CLAIMS_TO_ATTRIBUTES}

    def export_to_jwt(self) -> JwtExport:
        return {key: getattr(self, value) for key, value in self._JWT_CLAIMS_TO_ATTRIBUTES.items()}

    @field_validator('issued', 'expiry')
    @classmethod
    def validate_datetime(cls, value: datetime_module.datetime, info: ValidationInfo) -> datetime_module.datetime:
        return validate_and_normalize_datetime(value, info)

    @field_serializer('issued', 'expiry')
    def serialize_datetime(value: datetime_module.datetime) -> datetime_module.datetime:
        return value.replace(tzinfo=datetime_module.timezone.utc)


class AuthCredentialExport[IdType](TableExport[AuthCredential[IdType]]):
    _TABLE_MODEL: typing.ClassVar[typing.Type[AuthCredential]] = AuthCredential

    user_id: UserTypes.id
    issued: AuthCredentialTypes.issued
    expiry: AuthCredentialTypes.expiry


class AuthCredentialImport[IdType](TableImport[AuthCredential[IdType]]):
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


class AuthCredentialCreateAdmin[TTable: Table, IdType](AuthCredentialImport[IdType], TableCreateAdmin[TTable]):

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


class UserAccessTokenIDBase(IdObject[UserAccessTokenTypes.id]):
    id: UserAccessTokenTypes.id = Field(
        primary_key=True, index=True, unique=True, const=True)


class UserAccessToken(Table[UserAccessTokenTypes.id], UserAccessTokenIDBase, AuthCredential[UserAccessTokenTypes.id], table=True):
    type: typing.ClassVar[AuthCredentialTypes.type] = 'access_token'
    __tablename__ = 'user_access_token'

    user: User = Relationship(
        back_populates='user_access_tokens')

    @classmethod
    async def api_get(cls, **kwargs: Unpack[ApiGetMethodKwargs[UserAccessTokenTypes.id]]) -> typing.Self:

        user_access_token = await cls._basic_api_get(kwargs['session'], kwargs['id'])

        if not kwargs['admin']:
            if user_access_token.user_id != kwargs['authorized_user_id']:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=cls.not_found_message())

        return user_access_token

    @classmethod
    async def api_delete(cls, **kwargs: Unpack[ApiDeleteMethodKwargs[UserAccessTokenTypes.id]]) -> None:

        user_access_token = await cls._basic_api_get(kwargs['session'], kwargs['id'])

        if not kwargs['admin']:
            if user_access_token.user_id != kwargs['authorized_user_id']:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=cls.not_found_message())

        kwargs['session'].delete(user_access_token)
        kwargs['session'].commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)


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


class UserAccessTokenUpdate(UserAccessTokenImport):
    pass


class UserAccessTokenUpdateAdmin(UserAccessTokenUpdate, TableUpdateAdmin[UserAccessToken, UserAccessTokenTypes.id]):

    async def api_patch(self, **kwargs: Unpack[ApiPatchMethodKwargs[UserAccessTokenTypes.id]]) -> UserAccessToken:
        user_access_token = await UserAccessToken.api_get(**kwargs)
        user_access_token.sqlmodel_update(self.model_dump(exclude_unset=True))
        await user_access_token.add_to_db(kwargs['session'])
        return user_access_token


class UserAccessTokenCreate(UserAccessTokenImport):
    pass


class UserAccessTokenCreateAdmin(UserAccessTokenCreate, AuthCredentialCreateAdmin[UserAccessToken, UserAccessTokenTypes.id]):
    pass


# # ApiKey


class ApiKeyTypes(AuthCredentialTypes):
    id = str
    name = typing.Annotated[str, StringConstraints(
        min_length=1, max_length=256)]


class ApiKeyIdBase(IdObject[ApiKeyTypes.id]):
    id: ApiKeyTypes.id = Field(
        primary_key=True, index=True, unique=True, const=True)


class ApiKeyAvailable(BaseModel):
    name: ApiKeyTypes.name


class ApiKeyAvailableAdmin(ApiKeyAvailable):
    user_id: UserTypes.id


class ApiKey(Table[ApiKeyTypes.id], ApiKeyIdBase, AuthCredential[ApiKeyTypes.id], table=True):
    __tablename__ = 'api_key'

    name: ApiKeyTypes.name = Field()
    type: typing.ClassVar[AuthCredentialTypes.type] = 'api_key'

    user: User = Relationship(back_populates='api_keys')
    api_key_scopes: list['ApiKeyScope'] = Relationship(
        back_populates='api_key', cascade_delete=True)

    async def get_scope_ids(self) -> list[client.ScopeTypes.id]:
        return [api_key_scope.scope_id for api_key_scope in self.api_key_scopes]

    @classmethod
    async def is_available(cls, session: Session, api_key_available_admin: ApiKeyAvailableAdmin) -> bool:
        return not await cls.get_one_by_key_values(session, api_key_available_admin.model_dump())

    @classmethod
    async def api_get_is_available(cls, session: Session, api_key_available_admin: ApiKeyAvailableAdmin) -> None:
        if not await cls.is_available(session, api_key_available_admin):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=cls.already_exists_message())

    @classmethod
    async def api_get(cls, **kwargs: Unpack[ApiGetMethodKwargs[ApiKeyTypes.id]]) -> typing.Self:

        api_key = await cls._basic_api_get(kwargs['session'], kwargs['id'])
        if not kwargs['admin']:
            if api_key.user_id != kwargs['authorized_user_id']:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=cls.not_found_message())

        return api_key

    @classmethod
    async def api_delete(cls, **kwargs: Unpack[ApiDeleteMethodKwargs[ApiKeyTypes.id]]) -> None:

        api_key = await cls._basic_api_get(kwargs['session'], kwargs['id'])

        if not kwargs['admin']:
            if api_key.user_id != kwargs['authorized_user_id']:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=cls.not_found_message())

        kwargs['session'].delete(api_key)
        kwargs['session'].commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)


type PluralApiKeysDict = dict[ApiKeyTypes.id, ApiKey]


class ApiKeyExport(TableExport[ApiKey], AuthCredentialExport[ApiKeyTypes.id]):
    _TABLE_MODEL: typing.ClassVar[typing.Type[ApiKey]] = ApiKey
    name: ApiKeyTypes.name


class ApiKeyPublic(ApiKeyExport):
    pass


class ApiKeyPrivate(ApiKeyExport):
    pass


class ApiKeyImport(AuthCredentialImport[ApiKeyTypes.id]):
    _TABLE_MODEL: typing.ClassVar[typing.Type[ApiKey]] = ApiKey


class ApiKeyUpdate(ApiKeyImport):
    name: typing.Optional[ApiKeyTypes.name] = None


class ApiKeyUpdateAdmin(ApiKeyUpdate, TableUpdateAdmin[ApiKey, ApiKeyTypes.id]):
    async def api_patch(self, **kwargs: Unpack[ApiPatchMethodKwargs[ApiKeyTypes.id]]) -> ApiKey:
        api_key = await ApiKey.api_get(**kwargs)

        if 'name' in self.model_fields_set:
            if api_key.name != self.name:
                await ApiKey.api_get_is_available(kwargs['session'], ApiKeyAvailableAdmin(name=self.name, user_id=api_key.user_id))

        api_key.sqlmodel_update(self.model_dump(exclude_unset=True))
        await api_key.add_to_db(kwargs['session'])
        return api_key


class ApiKeyCreate(ApiKeyImport):
    name: ApiKeyTypes.name


class ApiKeyCreateAdmin(ApiKeyCreate, AuthCredentialCreateAdmin[ApiKey, ApiKeyTypes.id]):

    async def api_post(self, **kwargs: Unpack[ApiPostMethodKwargs]) -> ApiKey:
        await ApiKey.api_get_is_available(kwargs['session'], ApiKeyAvailableAdmin(name=self.name, user_id=kwargs['authorized_user_id']))
        api_key = await self.create()
        await api_key.add_to_db(kwargs['session'])
        return api_key


# AuthCredentialTypes

AUTH_CREDENTIAL_MODEL = UserAccessToken | ApiKey
AUTH_CREDENTIAL_MODEL_MAPPING: dict[AuthCredentialTypes.type, AUTH_CREDENTIAL_MODEL] = {
    UserAccessToken.type: UserAccessToken,
    ApiKey.type: ApiKey
}


#
# ApiKeyScope
#

class ApiKeyScopeTypes:
    api_key_id = ApiKeyTypes.id
    scope_id = client.ScopeTypes.id


type ApiKeyScopeID = typing.Annotated[tuple[ApiKeyScopeTypes.api_key_id,
                                            ApiKeyScopeTypes.scope_id], '(api_key_id, scope_id)'
                                      ]


class ApiKeyScopeIdBase(IdObject[ApiKeyScopeID]):
    _ID_COLS: typing.ClassVar[list[str]] = ['api_key_id', 'scope_id']

    api_key_id: ApiKeyScopeTypes.api_key_id = Field(
        index=True, foreign_key=ApiKey.__tablename__ + '.' + ApiKey._ID_COLS[0], ondelete='CASCADE')
    scope_id: ApiKeyScopeTypes.scope_id = Field(index=True)


class ApiKeyScope(Table[ApiKeyScopeID], ApiKeyScopeIdBase, table=True):
    __tablename__ = 'api_key_scope'
    __table_args__ = (
        PrimaryKeyConstraint('api_key_id', 'scope_id'),
    )

    api_key: ApiKey = Relationship(
        back_populates='api_key_scopes')

    @classmethod
    async def api_get(cls, **kwargs: Unpack[ApiGetMethodKwargs[ApiKeyScopeID]]) -> typing.Self:

        api_key_scope = await cls._basic_api_get(kwargs['session'], kwargs['id'])
        if not kwargs['admin']:
            if api_key_scope.api_key.user_id != kwargs['authorized_user_id']:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=cls.not_found_message())

        return api_key_scope

    @classmethod
    async def api_delete(cls, **kwargs: Unpack[ApiDeleteMethodKwargs[ApiKeyScopeID]]) -> None:

        api_key_scope = await cls.api_get(**kwargs)
        kwargs['session'].delete(api_key_scope)
        kwargs['session'].commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)


type PluralApiKeyScopesDict = dict[ApiKeyScopeID, ApiKeyScope]


class ApiKeyScopeExport(TableExport[ApiKeyScope], ApiKeyScopeIdBase):
    _TABLE_MODEL: typing.ClassVar[typing.Type[ApiKeyScope]] = ApiKeyScope


class ApiKeyScopePublic(ApiKeyScopeExport):
    pass


class ApiKeyScopePrivate(ApiKeyScopeExport):
    pass


class ApiKeyScopeCreateAdmin(ApiKeyScopeIdBase, TableCreateAdmin[ApiKeyScope]):
    _TABLE_MODEL: typing.ClassVar[typing.Type[ApiKeyScope]] = ApiKeyScope

    async def api_post(self, **kwargs: Unpack[ApiPostMethodKwargs]) -> ApiKeyScope:

        if await ApiKeyScope.get_one_by_id(kwargs['session'], self._id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail='Api key scope already exists')

        # if the given kwargs allow the user to access the api key, then they allow the user to create the ApiKeyScope
        api_key = await ApiKey.api_get(**kwargs, id=self.api_key_id)
        if self.scope_id not in kwargs['c'].user_role_id_scope_ids[api_key.user.user_role_id]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Scope doesn't exist for this user")

        existing_api_key_scope = await ApiKeyScope.get_one_by_id(kwargs['session'], self._id)
        if existing_api_key_scope:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Scope already exists for this API key")

        api_key_scope = await self.create()
        await api_key_scope.add_to_db(kwargs['session'])
        return api_key_scope

    async def create(self) -> ApiKeyScope:
        return ApiKeyScope(
            ** self.model_dump(),
        )

#
# Gallery
#


GalleryId = str


class GalleryTypes:
    id = GalleryId
    user_id = UserTypes.id

    # name can't start with the `YYYY-MM-DD ` pattern
    name = typing.Annotated[str, StringConstraints(
        min_length=1, max_length=256, pattern=re.compile(r'^(?!\d{4}-\d{2}-\d{2} ).*'))]
    visibility_level = client.VisibilityLevelTypes.id
    parent_id = GalleryId
    description = typing.Annotated[str, StringConstraints(
        min_length=0, max_length=20000)]
    date = datetime_module.date
    folder_name = str


class GalleryIdBase(IdObject[GalleryTypes.id]):
    id: GalleryTypes.id = Field(
        primary_key=True, index=True, unique=True, const=True)


class GalleryAvailable(BaseModel):
    name: GalleryTypes.name
    parent_id: typing.Optional[GalleryTypes.parent_id] = None
    date: typing.Optional[GalleryTypes.date] = None


class GalleryAvailableAdmin(GalleryAvailable):
    user_id: UserTypes.id


class Gallery(Table[GalleryTypes.id], GalleryIdBase, table=True):
    __tablename__ = 'gallery'

    name: GalleryTypes.name = Field()
    user_id: GalleryTypes.user_id = Field(
        index=True, foreign_key=User.__tablename__ + '.' + User._ID_COLS[0], ondelete='CASCADE')

    visibility_level: GalleryTypes.visibility_level = Field()
    parent_id: GalleryTypes.parent_id = Field(nullable=True, index=True,
                                              foreign_key=__tablename__ + '.id', ondelete='CASCADE')
    description: GalleryTypes.description = Field(nullable=True)
    date: GalleryTypes.date = Field(nullable=True)

    user: User = Relationship(back_populates='galleries')
    parent: typing.Optional['Gallery'] = Relationship(
        back_populates='children', sa_relationship_kwargs={'remote_side': 'Gallery.id'})
    children: list['Gallery'] = Relationship(
        back_populates='parent', cascade_delete=True)
    gallery_permissions: list['GalleryPermission'] = Relationship(
        back_populates='gallery', cascade_delete=True)
    files: list['File'] = Relationship(
        back_populates='gallery', cascade_delete=True)
    image_versions: list['ImageVersion'] = Relationship(
        back_populates='gallery', cascade_delete=True)

    @ property
    def folder_name(self) -> GalleryTypes.folder_name:
        if self.parent_id is None and self.name == 'root':
            return self.user_id
        if self.date is None:
            return self.name
        else:
            return self.date.isoformat() + ' ' + self.name

    @classmethod
    def get_date_and_name_from_folder_name(cls, folder_name: GalleryTypes.folder_name) -> tuple[GalleryTypes.date | None, GalleryTypes.name]:

        match = re.match(r'^(\d{4}-\d{2}-\d{2}) (.+)$', folder_name)
        if match:
            date_str, name = match.groups()
            date = datetime_module.date.fromisoformat(date_str)
            return (date, name)
        else:
            return (None, folder_name)

    async def get_dir(self, session: Session, root: pathlib.Path) -> pathlib.Path:

        if self.parent_id is None:
            return root / self.folder_name
        else:
            return (await self.parent.get_dir(session, root)) / self.folder_name

    async def get_parents(self, session: Session) -> list[typing.Self]:

        if self.parent_id is None:
            return []
        else:
            return (await self.parent.get_parents(session)) + [self.parent]

    @ classmethod
    async def api_get(cls, **kwargs: Unpack[ApiGetMethodKwargs[GalleryTypes.id]]) -> typing.Self:

        gallery = await cls._basic_api_get(kwargs['session'], kwargs['id'])

        if not kwargs['admin']:
            if gallery.visibility_level == kwargs['c'].visibility_level_name_mapping['private']:

                # user is not authorized, pretend it doesn't exist
                if not kwargs['authorized_user_id']:
                    raise HTTPException(status.HTTP_404_NOT_FOUND,
                                        detail=cls.not_found_message())

                # check user's permission
                if gallery.user_id != kwargs['authorized_user_id']:
                    gallery_permission = await GalleryPermission.get_one_by_id(kwargs['session'], (kwargs['id'], kwargs['authorized_user_id']))

                    # user has no access, pretend it doesn't exist
                    if not gallery_permission:
                        raise HTTPException(status.HTTP_404_NOT_FOUND,
                                            detail=cls.not_found_message())

        return gallery

    @ classmethod
    async def get_root_gallery(cls, session: Session, user_id: GalleryTypes.user_id) -> typing.Self | None:
        return await cls.get_one_by_key_values(session, {'user_id': user_id, 'parent_id': None})

    @ classmethod
    async def is_available(cls, session: Session, gallery_available_admin: GalleryAvailableAdmin) -> bool:
        return not await cls.get_one_by_key_values(session, gallery_available_admin.model_dump())

    @ classmethod
    async def api_get_is_available(cls, session: Session, gallery_available_admin: GalleryAvailableAdmin) -> None:
        if not await cls.is_available(session, gallery_available_admin):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=cls.already_exists_message())

    @ classmethod
    async def api_delete(cls, rmtree=True, **kwargs: Unpack[ApiDeleteMethodKwargs[GalleryTypes.id]]) -> None:

        gallery = await cls._basic_api_get(kwargs['session'], kwargs['id'])

        if not kwargs['admin']:
            if gallery.user_id != kwargs['authorized_user_id']:

                gallery_permission = await GalleryPermission.get_one_by_id(kwargs['session'], (kwargs['id'], kwargs['authorized_user_id']))

                if not gallery_permission and gallery.visibility_level == kwargs['c'].visibility_level_name_mapping['private']:
                    raise HTTPException(status.HTTP_404_NOT_FOUND,
                                        detail=cls.not_found_message())

                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to delete this gallery')

        if rmtree:
            shutil.rmtree((await gallery.get_dir(kwargs['session'], kwargs['c'].galleries_dir)))

        kwargs['session'].delete(gallery)
        kwargs['session'].commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    async def sync_with_local(self, session: Session, c: client.Client, dir: pathlib.Path) -> None:

        if not dir.exists():
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail='Directory not found')

        if self.folder_name != dir.name:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                detail='Folder name does not match gallery name')

        files: list[pathlib.Path] = []
        dirs: list[pathlib.Path] = []
        for item in dir.iterdir():
            if item.is_dir():
                dirs.append(item)
            if item.is_file():
                files.append(item)

        # Add new galleries, remove old ones
        local_galleries_by_folder_name = {
            item.name: item for item in dirs}
        db_galleries_by_folder_name = {
            gallery.folder_name: gallery for gallery in self.children}

        local_galleries_folder_names = set(
            local_galleries_by_folder_name.keys())
        db_galleries_folder_names = set(db_galleries_by_folder_name.keys())

        to_add = local_galleries_folder_names - db_galleries_folder_names
        to_remove = db_galleries_folder_names - local_galleries_folder_names

        for folder_name in to_remove:
            gallery = db_galleries_by_folder_name[folder_name]
            await Gallery.api_delete(session=session, c=c, id=gallery.id, authorized_user_id=self.user_id, admin=False, rmtree=False)

        for folder_name in to_add:
            date, name = self.get_date_and_name_from_folder_name(folder_name)
            new_gallery = await GalleryCreateAdmin(name=name, user_id=self.user_id, visibility_level=self.visibility_level, parent_id=self.id, date=date).api_post(
                session=session, c=c, authorized_user_id=self.user_id, admin=False, mkdir=False)

        # add new files, remove old ones
        local_file_by_names = {
            file.name: file for file in files}
        db_files_by_names = {
            file.name: file for file in self.files}

        local_file_names = set(local_file_by_names.keys())
        db_file_names = set(db_files_by_names.keys())

        to_add = local_file_names - db_file_names
        to_remove = db_file_names - local_file_names

        for file_name in to_remove:
            file = db_files_by_names[file_name]

            # if this is the last image tied to that version, delete the version too
            if file.suffix in ImageFileMetadata._SUFFIXES:
                image_version = await ImageVersion.get_one_by_id(session, file.image_file_metadata.version_id)
                if len(image_version.image_file_metadatas) == 1:
                    await ImageVersion.api_delete(session=session, c=c, id=image_version.id, authorized_user_id=self.user_id, admin=False)

            await File.api_delete(session=session, c=c, id=file.id, authorized_user_id=self.user_id, admin=False, unlink=False)

        image_files: list[File] = []

        for file_name in to_add:
            stem = local_file_by_names[file_name].stem
            suffix = ''.join(suffixes) if (
                suffixes := local_file_by_names[file_name].suffixes) else None

            new_file = await FileCreateAdmin(stem=stem, suffix=suffix, gallery_id=self.id, size=local_file_by_names[file_name].stat().st_size).api_post(
                session=session, c=c, authorized_user_id=self.user_id, admin=False)

            # rename the file, just to make sure the suffix is lowercase
            local_file_by_names[file_name].rename(
                local_file_by_names[file_name].with_name(new_file.name))

            if suffix in ImageFileMetadata._SUFFIXES:
                image_files.append(new_file)

        # loop through files twice, adding the original images first
        for original_images in [True, False]:
            for image_file in image_files:

                base_name, version, scale = ImageFileMetadata.parse_file_stem(
                    image_file.stem)

                if original_images == (version == None):

                    parent_id = None
                    if version is not None:
                        image_version_og = await ImageVersion.get_one_by_key_values(session, {'gallery_id': self.id, 'base_name': base_name, 'version': None})

                        # if an original exists, assume the version wants to link as the parent
                        if image_version_og:
                            parent_id = image_version_og._id

                    image_version_kwargs = {
                        'gallery_id': self.id,
                        'base_name': base_name if parent_id is None else None,
                        'version': version,
                        'parent_id': parent_id
                    }

                    image_version = await ImageVersion.get_one_by_key_values(session, image_version_kwargs)

                    # this if the first file of this version
                    if not image_version:
                        image_version = await ImageVersionCreateAdmin(**image_version_kwargs).api_post(
                            session=session, c=c, authorized_user_id=self.user_id, admin=False)

                    image_file_metadata = await ImageFileMetadataCreateAdmin(file_id=image_file.id, version_id=image_version.id, scale=scale).api_post(
                        session=session, c=c, authorized_user_id=self.user_id, admin=False)

        # recursively sync children
        for child in self.children:
            await child.sync_with_local(session, c, dir / child.folder_name)


type PluralGalleriesDict = dict[GalleryTypes.id, Gallery]


# Export Types


class GalleryExport(TableExport[Gallery]):
    _TABLE_MODEL: typing.ClassVar[typing.Type[Gallery]] = Gallery

    id: GalleryTypes.id
    user_id: GalleryTypes.user_id
    name: GalleryTypes.name
    parent_id: GalleryTypes.parent_id | None
    description: GalleryTypes.description | None
    date: GalleryTypes.date | None


class GalleryPublic(GalleryExport):
    pass


class GalleryPrivate(GalleryExport):
    visibility_level: GalleryTypes.visibility_level


# Import Types

class GalleryImport(TableImport[Gallery]):
    _TABLE_MODEL: typing.ClassVar[typing.Type[Gallery]] = Gallery


class GalleryUpdate(GalleryImport):
    name: typing.Optional[GalleryTypes.name] = None
    user_id: typing.Optional[GalleryTypes.user_id] = None
    visibility_level: typing.Optional[GalleryTypes.visibility_level] = None
    parent_id: typing.Optional[GalleryTypes.parent_id] = None
    description: typing.Optional[GalleryTypes.description] = None
    date: typing.Optional[GalleryTypes.date] = None


class GalleryUpdateAdmin(GalleryUpdate, TableUpdateAdmin[Gallery, GalleryTypes.id]):

    async def api_patch(self, **kwargs: Unpack[ApiPatchMethodKwargs[GalleryTypes.id]]) -> Gallery:

        # if it doesn't exist, throw 404

        gallery = await self._TABLE_MODEL._basic_api_get(kwargs['session'], kwargs['id'])
        if not kwargs['admin']:
            if kwargs['authorized_user_id'] != gallery.user_id:
                gallery_permission = await GalleryPermission.get_one_by_id(kwargs['session'], (kwargs['id'], kwargs['authorized_user_id']))

                # if the gallery is private and user has no access, pretend it doesn't exist
                if not gallery_permission and gallery.visibility_level == kwargs['c'].visibility_level_name_mapping['private']:
                    raise HTTPException(status.HTTP_404_NOT_FOUND,
                                        detail=self._TABLE_MODEL.not_found_message())

                # for public galleries, or for private galleries where the user lacks edit access
                if gallery_permission.permission_level < kwargs['c'].permission_level_name_mapping['editor']:
                    raise HTTPException(
                        status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to patch this gallery')

        # raise HTTP 409 if the gallery already exists
        await Gallery.api_get_is_available(kwargs['session'], GalleryAvailableAdmin(**{
            **gallery.model_dump(include=GalleryAvailableAdmin.model_fields.keys()), **self.model_dump(include=list(GalleryAvailableAdmin.model_fields.keys()), exclude_unset=True)
        }))

        rename_folder = False

        # rename the folder
        if 'name' in self.model_fields_set or 'date' in self.model_fields_set or 'parent_id' in self.model_fields_set:
            rename_folder = True
            original_dir = await gallery.get_dir(kwargs['session'], kwargs['c'].galleries_dir)

        gallery.sqlmodel_update(self.model_dump(exclude_unset=True))

        if rename_folder:
            new_dir = (await gallery.get_dir(kwargs['session'], kwargs['c'].galleries_dir)).parent / gallery.folder_name
            original_dir.rename(new_dir)

        await gallery.add_to_db(kwargs['session'])
        return gallery


class GalleryCreate(GalleryImport):
    name: GalleryTypes.name
    user_id: GalleryTypes.user_id
    visibility_level: GalleryTypes.visibility_level
    parent_id: typing.Optional[GalleryTypes.parent_id] = None
    description: typing.Optional[GalleryTypes.description] = None
    date: typing.Optional[GalleryTypes.date] = None


class GalleryCreateAdmin(GalleryCreate, TableCreateAdmin[Gallery]):

    async def api_post(self, mkdir=True, **kwargs: Unpack[ApiPostMethodKwargs]) -> Gallery:

        await Gallery.api_get_is_available(kwargs['session'], GalleryAvailableAdmin(**self.model_dump(include=['name', 'parent_id', 'date', 'user_id'])))
        gallery = await self.create()
        await gallery.add_to_db(kwargs['session'])

        if mkdir:
            (await gallery.get_dir(kwargs['session'], kwargs['c'].galleries_dir)).mkdir()

        return gallery

#
# GalleryPermission
#


class GalleryPermissionTypes:
    gallery_id = GalleryTypes.id
    user_id = UserTypes.id
    permission_level = client.PermissionLevelTypes.id


type GalleryPermissionId = typing.Annotated[tuple[GalleryPermissionTypes.gallery_id,
                                                  GalleryPermissionTypes.user_id], '(gallery_id, user_id)']


class GalleryPermissionIdBase(IdObject[GalleryPermissionId]):
    _ID_COLS: typing.ClassVar[list[str]] = ['gallery_id', 'user_id']

    gallery_id: GalleryPermissionTypes.gallery_id = Field(
        primary_key=True, index=True, foreign_key=Gallery.__tablename__ + '.' + Gallery._ID_COLS[0], ondelete='CASCADE')
    user_id: GalleryPermissionTypes.user_id = Field(
        primary_key=True, index=True, foreign_key=User.__tablename__ + '.' + User._ID_COLS[0], ondelete='CASCADE')


class GalleryPermission(Table[GalleryPermissionId], GalleryPermissionIdBase, table=True):
    __tablename__ = 'gallery_permission'
    __table_args__ = (
        PrimaryKeyConstraint('gallery_id', 'user_id'),
    )

    permission_level: GalleryPermissionTypes.permission_level = Field()

    gallery: Gallery = Relationship(back_populates='gallery_permissions')
    user: User = Relationship(back_populates='gallery_permissions')

    @ classmethod
    async def api_get(cls, method='get', **kwargs: Unpack[ApiGetMethodKwargs[GalleryPermissionId]]) -> typing.Self:

        gallery_permission = await cls._basic_api_get(kwargs['session'], kwargs['id'])

        if not kwargs['admin']:
            gallery = await Gallery.get_one_by_id(kwargs['session'], kwargs['id'][0])
            if gallery.user_id != kwargs['authorized_user_id']:
                authorized_user_gallery_permission = await cls.get_one_by_id(kwargs['session'], (kwargs['id'][0], kwargs['authorized_user_id']))

                if authorized_user_gallery_permission or gallery.visibility_level == kwargs['c'].visibility_level_name_mapping['public']:
                    raise HTTPException(
                        status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to ' + method + ' this gallery permission')
                else:
                    raise HTTPException(
                        status.HTTP_404_NOT_FOUND, detail=cls.not_found_message())

        return gallery_permission

    @ classmethod
    async def api_delete(cls, **kwargs: Unpack[ApiDeleteMethodKwargs[GalleryPermissionId]]) -> None:

        gallery_permission = await cls.api_get(method='delete', **kwargs)
        kwargs['session'].delete(gallery_permission)
        kwargs['session'].commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)


type PluralGalleryPermissionsDict = dict[GalleryPermissionId,
                                         GalleryPermission]


class GalleryPermissionExport(TableExport[GalleryPermission]):
    _TABLE_MODEL: typing.ClassVar[typing.Type[GalleryPermission]
                                  ] = GalleryPermission

    gallery_id: GalleryPermissionTypes.gallery_id
    user_id: GalleryPermissionTypes.user_id
    permission_level: GalleryPermissionTypes.permission_level


class GalleryPermissionPublic(GalleryPermissionExport):
    pass


class GalleryPermissionPrivate(GalleryPermissionExport):
    pass


class GalleryPermissionImport(TableImport[GalleryPermission]):
    _TABLE_MODEL: typing.ClassVar[typing.Type[GalleryPermission]
                                  ] = GalleryPermission


class GalleryPermissionUpdateAdmin(GalleryPermissionImport, TableUpdateAdmin[GalleryPermission, GalleryPermissionId]):
    permission_level: typing.Optional[GalleryPermissionTypes.permission_level]

    async def api_patch(self, **kwargs: Unpack[ApiPatchMethodKwargs[GalleryPermissionId]]) -> GalleryPermission:
        gallery_permission = await GalleryPermission.api_get(method='patch', **kwargs)
        gallery_permission.sqlmodel_update(self.model_dump(exclude_unset=True))
        await gallery_permission.add_to_db(kwargs['session'])
        return gallery_permission


class GalleryPermissionCreateAdmin(GalleryPermissionImport, GalleryPermissionIdBase, TableCreateAdmin[GalleryPermission]):
    permission_level: GalleryPermissionTypes.permission_level

    async def api_post(self, **kwargs: Unpack[ApiPostMethodKwargs]) -> GalleryPermission:
        if await GalleryPermission.get_one_by_id(kwargs['session'], self.model_dump()):
            raise HTTPException(
                status.HTTP_409_CONFLICT, detail='Gallery permission already exists')

        gallery_permission = await self.create()
        await gallery_permission.add_to_db(kwargs['session'])
        return gallery_permission

    async def create(self) -> GalleryPermission:
        return GalleryPermission(
            ** self.model_dump(),
        )


#
# File
#


class FileTypes:
    id = str
    stem = str
    suffix = typing.Annotated[str, StringConstraints(
        to_lower=True)]
    size = int
    gallery_id = GalleryTypes.id


class FileIdBase(IdObject[FileTypes.id]):
    id: FileTypes.id = Field(
        primary_key=True, index=True, unique=True, const=True)


class File(Table[FileTypes.id], FileIdBase, table=True):
    __tablename__ = 'file'

    stem: FileTypes.stem
    suffix: FileTypes.suffix = Field(nullable=True)
    gallery_id: FileTypes.gallery_id = Field(
        index=True, foreign_key=Gallery.__tablename__ + '.' + Gallery._ID_COLS[0], ondelete='CASCADE')
    size: FileTypes.size = Field(nullable=True)

    gallery: Gallery = Relationship(back_populates='files')
    image_file_metadata: typing.Optional['ImageFileMetadata'] = Relationship(
        back_populates='file', cascade_delete=True)

    @property
    def name(self) -> str:
        return self.stem + self.suffix

    @classmethod
    async def api_get(cls, **kwargs: Unpack[ApiGetMethodKwargs[FileTypes.id]]) -> typing.Self:
        return await super().api_get(**kwargs)

    @classmethod
    async def api_delete(cls, unlink=True, **kwargs: Unpack[ApiDeleteMethodKwargs[FileTypes.id]]) -> None:
        return await super().api_delete(**kwargs)


type PluralFilesDict = dict[FileTypes.id, File]


class FileExport(TableExport[File]):
    _TABLE_MODEL: typing.ClassVar[typing.Type[File]] = File

    id: FileTypes.id
    stem: FileTypes.stem
    suffix: FileTypes.suffix | None
    size: FileTypes.size


class FilePublic(FileExport):
    pass


class FilePrivate(FileExport):
    pass


class FileImport(TableImport[File]):
    _TABLE_MODEL: typing.ClassVar[typing.Type[File]] = File


class FileUpdate(FileImport):
    stem: typing.Optional[FileTypes.stem] = None
    gallery_id: typing.Optional[FileTypes.gallery_id] = None


class FileUpdateAdmin(FileUpdate, TableUpdateAdmin[File, FileTypes.id]):
    pass


class FileCreate(FileImport):
    stem: FileTypes.stem
    suffix: FileTypes.suffix | None
    gallery_id: FileTypes.gallery_id
    size: FileTypes.size | None


class FileCreateAdmin(FileCreate, TableCreateAdmin[File]):
    pass


#
# Version
#
ImageVersionId = str


class ImageVersionTypes:
    id = ImageVersionId
    gallery_id = GalleryTypes.id
    base_name = typing.Annotated[str, StringConstraints(
        # prohibit underscore
        min_length=1, max_length=240, pattern=re.compile(r'^(?!.*_).+$')
    )]
    version = typing.Annotated[str, StringConstraints(
        # version cannot be exactly two digits
        pattern=re.compile(r'^(?!\d{2}$).+$'))]
    parent_id = ImageVersionId
    datetime = datetime_module.datetime
    description = typing.Annotated[str, StringConstraints(
        min_length=0, max_length=20000)]
    aspect_ratio = float
    average_color = str


class ImageVersionIdBase(IdObject[ImageVersionId]):
    id: ImageVersionId = Field(
        primary_key=True, index=True, unique=True, const=True)


class ImageVersion(Table[ImageVersionTypes.id], ImageVersionIdBase, table=True):
    __tablename__ = 'image_version'

    base_name: ImageVersionTypes.base_name = Field(nullable=True, index=True)
    parent_id: ImageVersionTypes.parent_id = Field(
        nullable=True, index=True, foreign_key=__tablename__ + '.id', ondelete='SET NULL')

    # BW, Edit1, etc. Original version is null
    version: ImageVersionTypes.version = Field(nullable=True)
    gallery_id: ImageVersionTypes.gallery_id = Field(
        index=True, foreign_key=Gallery.__tablename__ + '.' + Gallery._ID_COLS[0], ondelete='CASCADE')

    datetime: ImageVersionTypes.datetime = Field(nullable=True)
    description: ImageVersionTypes.description = Field(nullable=True)
    aspect_ratio: ImageVersionTypes.aspect_ratio = Field(nullable=True)
    average_color: ImageVersionTypes.average_color = Field(nullable=True)

    parent: typing.Optional['ImageVersion'] = Relationship(
        back_populates='children', sa_relationship_kwargs={'remote_side': 'ImageVersion.id'})
    children: list['ImageVersion'] = Relationship(
        back_populates='parent')

    image_file_metadatas: list['ImageFileMetadata'] = Relationship(
        back_populates='version')
    gallery: Gallery = Relationship(
        back_populates='image_versions')

    @model_validator(mode='after')
    def validate_model(self, info: ValidationInfo) -> None:
        if self.base_name is None and self.parent_id is None:
            raise ValueError('Unnamed versions must have a parent_id')

    @ field_validator('datetime')
    @ classmethod
    def validate_datetime(cls, value: datetime_module.datetime, info: ValidationInfo) -> datetime_module.datetime:
        return validate_and_normalize_datetime(value, info)

    @ field_serializer('datetime')
    def serialize_datetime(value: datetime_module.datetime) -> datetime_module.datetime:
        return value.replace(tzinfo=datetime_module.timezone.utc)

    async def get_root_base_name(self) -> ImageVersionTypes.base_name:
        if self.base_name is not None:
            return self.base_name
        else:
            if self.parent_id is not None:
                return (await self.parent.get_root_base_name())
            else:
                raise ValueError('Unnamed versions must have a parent_id')


type PluralImageVersionsDict = dict[ImageVersionTypes.id, ImageVersion]


# Export Types


class ImageVersionExport(TableExport[ImageVersion]):
    _TABLE_MODEL: typing.ClassVar[typing.Type[ImageVersion]] = ImageVersion

    id: ImageVersionTypes.id
    base_name: ImageVersionTypes.base_name | None
    parent_id: ImageVersionTypes.parent_id | None
    version: ImageVersionTypes.version | None
    datetime: ImageVersionTypes.datetime | None
    description: ImageVersionTypes.description | None
    aspect_ratio: ImageVersionTypes.aspect_ratio | None


class ImageVersionPublic(ImageVersionExport):
    pass


class ImageVersionPublic(ImageVersionExport):
    pass


class ImageVersionImport(TableImport[ImageVersion]):
    _TABLE_MODEL: typing.ClassVar[typing.Type[ImageVersion]] = ImageVersion
    base_name: typing.Optional[ImageVersionTypes.base_name] = None
    parent_id: typing.Optional[ImageVersionTypes.parent_id] = None
    version: typing.Optional[ImageVersionTypes.version] = None
    datetime: typing.Optional[ImageVersionTypes.datetime] = None
    description: typing.Optional[ImageVersionTypes.description] = None


class ImageVersionUpdate(ImageVersionImport, ImageVersionIdBase):
    pass


class ImageVersionUpdateAdmin(ImageVersionUpdate, TableUpdateAdmin[ImageVersion, ImageVersionTypes.id]):
    _TABLE_MODEL: typing.ClassVar[typing.Type[ImageVersion]] = ImageVersion


class ImageVersionCreate(ImageVersionImport):
    pass


class ImageVersionCreateAdmin(ImageVersionCreate, TableCreateAdmin[ImageVersion]):
    _TABLE_MODEL: typing.ClassVar[typing.Type[ImageVersion]] = ImageVersion

    gallery_id: ImageVersionTypes.gallery_id
    base_name: typing.Optional[ImageVersionTypes.base_name] = None
    version: typing.Optional[ImageVersionTypes.version] = None
    parent_id: typing.Optional[ImageVersionTypes.parent_id] = None
    datetime: typing.Optional[ImageVersionTypes.datetime] = None
    description: typing.Optional[ImageVersionTypes.description] = None
    aspect_ratio: typing.Optional[ImageVersionTypes.aspect_ratio] = None
    average_color: typing.Optional[ImageVersionTypes.average_color] = None


#
# Image File Metadata
#

class ImageFileMetadataTypes:
    file_id = FileTypes.id
    version_id = ImageVersionTypes.id
    scale = int


class ImageFileMetadataIdBase(IdObject[ImageFileMetadataTypes.file_id]):
    _ID_COLS: typing.ClassVar[list[str]] = ['file_id']

    file_id: ImageFileMetadataTypes.file_id = Field(
        primary_key=True, index=True, unique=True, const=True, foreign_key=File.__tablename__ + '.' + File._ID_COLS[0], ondelete='CASCADE')


class ImageFileMetadata(Table[ImageFileMetadataTypes.file_id], ImageFileMetadataIdBase, table=True):
    __tablename__ = 'image_file_metadata'

    _SUFFIXES: typing.ClassVar[set[str]] = {
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}

    version_id: ImageFileMetadataTypes.version_id = Field(
        index=True, foreign_key=ImageVersion.__tablename__ + '.' + ImageVersion._ID_COLS[0], ondelete='CASCADE')

    scale: ImageFileMetadataTypes.scale = Field(nullable=True, ge=1, le=99)
    version: ImageVersion = Relationship(back_populates='image_file_metadatas')
    file: File = Relationship(
        back_populates='image_file_metadata')

    @classmethod
    def parse_file_stem(cls, file_stem: str) -> tuple[ImageVersionTypes.base_name, ImageVersionTypes.version | None, ImageFileMetadataTypes.scale | None]:

        scale = None
        if match := re.search(r'_(\d{2})$', file_stem):
            scale = int(match.group(1))
            file_stem = file_stem[:match.start()]

        version = None
        if match := re.search(r'_(.+)$', file_stem):
            version = match.group(1)
            file_stem = file_stem[:match.start()]

        return file_stem, version, scale


ImageFileMetadatasPluralDict = dict[ImageFileMetadataTypes.file_id,
                                    ImageFileMetadata]

# Export Types


class ImageFileMetadataExport(TableExport[ImageFileMetadata]):
    _TABLE_MODEL: typing.ClassVar[typing.Type[ImageFileMetadata]
                                  ] = ImageFileMetadata

    file_id: ImageFileMetadataTypes.file_id
    version_id: ImageFileMetadataTypes.version_id
    scale: ImageFileMetadataTypes.scale | None


class ImageFileMetadataPublic(ImageFileMetadataExport):
    pass


class ImageFileMetadataPrivate(ImageFileMetadataExport):
    pass


class ImageFileMetadataImport(TableImport[ImageFileMetadata]):
    _TABLE_MODEL: typing.ClassVar[typing.Type[ImageFileMetadata]
                                  ] = ImageFileMetadata


class ImageFileMetadataUpdate(ImageFileMetadataImport, ImageFileMetadataIdBase):
    pass


class ImageFileMetadataUpdateAdmin(ImageFileMetadataUpdate, TableUpdateAdmin[ImageFileMetadata, ImageFileMetadataTypes.file_id]):
    pass


class ImageFileMetadataCreate(ImageFileMetadataImport):
    file_id: ImageFileMetadataTypes.file_id
    version_id: ImageFileMetadataTypes.version_id
    scale: typing.Optional[ImageFileMetadataTypes.scale] = Field(
        default=None, ge=1, le=99)


class ImageFileMetadataCreateAdmin(ImageFileMetadataCreate, TableCreateAdmin[ImageFileMetadata]):

    async def create(self) -> ImageFileMetadata:
        return self._TABLE_MODEL(** self.model_dump())


if __name__ == '__main__':
    print()
