import string
import secrets
from pydantic import BaseModel, field_validator
import typing
from typing import Unpack, TypeVarTuple
import uuid
from fastapi import HTTPException, status, Response, APIRouter, Query

# from sqlmodel import SQLModel, Field, Column, Session, select, delete, Relationship

from sqlalchemy import PrimaryKeyConstraint, and_, or_, event, Column, Table
from sqlalchemy.types import Integer, String
from sqlalchemy.sql import select
from sqlalchemy.orm import declarative_base, declared_attr, Session
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.engine import Result

from pydantic import BaseModel, EmailStr, constr, StringConstraints, field_validator, ValidationInfo, ValidatorFunctionWrapHandler, ValidationError, field_serializer, model_validator, conint
from pydantic.functional_validators import WrapValidator
from gallery import utils, types, config
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
from functools import wraps, lru_cache


Base = declarative_base()


def api_endpoint(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


class MethodParamsBase(typing.TypedDict):
    session: Session
    c: client.Client
    authorized_user_id: typing.Optional[types.UserTypes.id]
    admin: bool


class MethodParamsBaseWithId[IdType](MethodParamsBase):
    id: IdType


class PostParams[TPostModel: BaseModel](MethodParamsBase):
    create_model: TPostModel


class GetParams[IdType](MethodParamsBaseWithId[IdType]):
    pass


class PatchParams[IdType, TPatchModel: BaseModel](MethodParamsBaseWithId[IdType]):
    update_model: TPatchModel


class DeleteParams[IdType](MethodParamsBaseWithId[IdType]):
    pass


class CheckAuthorizationExistingParams[IdType](MethodParamsBaseWithId[IdType]):
    method: typing.Literal['get', 'patch', 'delete']


class Pagination(BaseModel):
    limit: int
    offset: int


class TableExport(BaseModel):
    class Config:
        from_attributes = True


class TableDB(Base):
    __abstract__ = True


class IdObject[IdType]:
    _ID_COLS: typing.ClassVar[list[str]] = ['id']

    @property
    def _id(self) -> IdType:
        """Return the ID of the model"""

        if len(self._ID_COLS) > 1:
            return tuple(getattr(self, key) for key in self._ID_COLS)
        else:
            return getattr(self, self._ID_COLS[0])

    @classmethod
    def generate_id(cls) -> IdType:
        """Generate a new ID for the model"""

        if len(cls._ID_COLS) > 1:
            return tuple(str(uuid.uuid4()) for _ in range(len(cls._ID_COLS)))
        else:
            return str(uuid.uuid4())

    @classmethod
    def export_plural_to_dict(cls, items: collections.abc.Iterable[typing.Self]) -> dict[IdType, typing.Self]:
        return {item._id: item for item in items}


class TableService[
    T: 'Table',
    IdType,
    TCreateMethodModel: BaseModel,
    TUpdateMethodModel: BaseModel,
    TOrderBy
](IdObject[IdType]):

    _ROUTER_TAG: typing.ClassVar[str] = 'asdf'
    _TABLE_DB: typing.ClassVar = typing.Any

    @classmethod
    def _get_by_id(cls, session: Session, id: IdType) -> T | None:

        query = select(cls)
        if len(cls._ID_COLS) == 1:
            id = [id]

        for i in range(len(cls._ID_COLS)):
            field: InstrumentedAttribute = getattr(cls, cls._ID_COLS[i])
            query = query.where(field == id[i])

        return session.execute(query).one_or_none()

    @classmethod
    async def _create(cls, session: Session, create_model: T) -> T:
        session.add(create_model)
        session.commit()
        session.refresh(create_model)
        return create_model

    async def _update(self, session: Session, patch_model: T):
        pass

        # for key, value in patch_model.model_dump(exclude_unset=True):
        #     setattr(self, key, value)

    async def delete(self, id: IdType):
        pass

    # async def create(self):

    #     id = cls.generate_id()
    #     if len(cls._ID_COLS) == 1:
    #         id = [id]

    #     return cls(
    #         **{key: value for key, value in zip(
    #             cls._ID_COLS, id)},
    #         **post_model.model_dump()
    #     )

    #     pass

    # @classmethod
    # @lru_cache(maxsize=None)
    # def not_found_message(cls) -> str:
    #     return f'{cls.__name__} not found'

    # @classmethod
    # @lru_cache(maxsize=None)
    # def already_exists_message(cls) -> str:
    #     return f'{cls.__name__} already exists'

    # @classmethod
    # @lru_cache(maxsize=None)
    # def not_found_exception(cls) -> HTTPException:
    #     return HTTPException(status.HTTP_404_NOT_FOUND, detail=cls.not_found_message())

    # @classmethod
    # @lru_cache(maxsize=None)
    # def already_exists_exception(cls) -> HTTPException:
    #     return HTTPException(status.HTTP_409_CONFLICT, detail=cls.already_exists_message())

    # @classmethod
    # @lru_cache(maxsize=None)
    # def get_responses(cls):
    #     return {}

    # @classmethod
    # @lru_cache(maxsize=None)
    # def post_responses(cls):
    #     return {}

    # @classmethod
    # @lru_cache(maxsize=None)
    # def patch_responses(cls):
    #     return {}

    # @classmethod
    # @lru_cache(maxsize=None)
    # def delete_responses(cls):
    #     return {}

    # @classmethod
    # def make_order_by_dependency(cls):

    #     def order_by_depends(
    #             order_by: list[TOrderBy] = Query(
    #                 [], description='Ordered series of fields to sort the results by, in the order they should be applied'),
    #             order_by_desc: list[TOrderBy] = Query(
    #                 [], description='Unordered series of fields which should be sorted in a descending manner, must be a subset of "order_by" fields')
    #     ) -> list[OrderBy[TOrderBy]]:

    #         order_by_set = set(order_by)
    #         order_by_desc_set = set(order_by_desc)

    #         if not order_by_desc_set.issubset(order_by_set):
    #             raise HTTPException(status.HTTP_400_BAD_REQUEST,
    #                                 detail='"order_by_desc" fields must be a subset of "order_by" fields')

    #         return [
    #             OrderBy[TOrderBy](
    #                 field=field, ascending=field not in order_by_desc_set)
    #             for field in order_by
    #         ]

    #     return order_by_depends

    # @classmethod
    # def _build_conditions(cls, filters: dict[str, typing.Any]):

    #     conditions = []
    #     for key in filters:
    #         value = filters[key]
    #         field: InstrumentedAttribute = getattr(cls, key)

    #         if isinstance(value, list):
    #             conditions.append(field.in_(value))
    #         else:
    #             conditions.append(field == value)

    #     return and_(*conditions)

    # @classmethod
    # def _build_order_by[TQuery: Select, TOrderBy](cls, query: TQuery, order_by: list[OrderBy[TOrderBy]]):
    #     for order in order_by:
    #         field: InstrumentedAttribute = getattr(cls, order.field)
    #         if order.ascending:
    #             query = query.order_by(field.asc())
    #         else:
    #             query = query.order_by(field.desc())

    #     return query

    # async def _check_authorization_existing(self, params: CheckAuthorizationExistingParams[IdType]):
    #     pass

    # @classmethod
    # async def _check_authorization_post(cls, params: PostParams):
    #     pass

    # async def _check_validation_delete(self, params: DeleteParams):
    #     pass

    # async def _check_validation_patch(self, params: PatchParams):
    #     pass

    # @classmethod
    # async def _check_validation_post(cls, params: PostParams):
    #     pass

    # @classmethod
    # @api_endpoint
    # async def api_get(cls, params: GetParams):
    #     """Get a model by its ID, raise an exception if not found"""

    #     instance = await cls.read(params.session, params.id)
    #     if not instance:
    #         raise cls.not_found_exception()

    #     # use model construct to bypass the validation
    #     await instance._check_authorization_existing(CheckAuthorizationExistingParams.model_construct(**params.model_dump(), method='get'))
    #     return instance

    # @classmethod
    # @api_endpoint
    # async def api_post(cls, params: PostParams):
    #     await cls._check_authorization_post(params)
    #     await cls._check_validation_post(params)

    #     instance = await cls.create(params)
    #     params.session.add(instance)
    #     params.session.commit()
    #     params.session.refresh(instance)
    #     return instance

    # @classmethod
    # @api_endpoint
    # async def api_patch(self, params: PatchParams):

    #     instance = await self.read(params.session, params.id)
    #     if not instance:
    #         raise self.not_found_exception()

    #     # use model construct to bypass the validation
    #     await instance._check_authorization_existing(CheckAuthorizationExistingParams.model_construct(**params.model_dump(), method='patch'))
    #     await instance._check_validation_patch(params)
    #     await instance.update(params)

    #     params.session.add(instance)
    #     params.session.commit()
    #     params.session.refresh(instance)
    #     return instance

    # @classmethod
    # @api_endpoint
    # async def api_delete(cls, params: DeleteParams) -> None:

    #     instance = await cls.read(params.session, params.id)
    #     if not instance:
    #         raise cls.not_found_exception()

    #     # use model construct to bypass the validation
    #     await instance._check_authorization_existing(CheckAuthorizationExistingParams.model_construct(**params.model_dump(), method='delete'))
    #     await instance._check_validation_delete(params)
    #     await instance.delete(params)

    #     params.session.delete(instance)
    #     params.session.commit()
    #     return Response(status_code=status.HTTP_204_NO_CONTENT)


class UserDB(TableDB):
    __tablename__ = 'user'
    id = Column(String, primary_key=True, index=True, unique=True)
    email = Column(String, index=True, unique=True)
    phone_number = Column(String, unique=True, nullable=True)
    username = Column(String, index=True, unique=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    user_role_id = Column(Integer)


class UserIdBase(IdObject[types.UserTypes.id]):
    id: types.UserTypes.id


class UserImport(BaseModel):
    phone_number: typing.Optional[types.UserTypes.phone_number] = None
    username: typing.Optional[types.UserTypes.username] = None
    password: typing.Optional[types.UserTypes.password] = None


class UserUpdate(UserImport):
    email: typing.Optional[types.UserTypes.email] = None


class UserAdminUpdate(UserUpdate):
    user_role_id: typing.Optional[types.UserTypes.user_role_id] = None


class UserCreate(UserImport):
    email: types.UserTypes.email


class UserAdminCreate(UserCreate):
    user_role_id: types.UserTypes.user_role_id


# class User(Table['User', types.UserTypes.id, UserAdminCreate, BaseModel, BaseModel, UserAdminUpdate, BaseModel, BaseModel, typing.Literal[()]], UserIdBase, table=True):
class User(TableService['User', types.UserTypes.id, UserAdminCreate, UserAdminUpdate, typing.Literal[()]]):

    _DBClass = UserDB

    # api_keys: list['ApiKey'] = Relationship(
    #     back_populates='user', cascade_delete=True)
    # user_access_tokens: list['UserAccessToken'] = Relationship(
    #     back_populates='user', cascade_delete=True)
    # galleries: list['Gallery'] = Relationship(
    #     back_populates='user', cascade_delete=True)
    # gallery_permissions: list['GalleryPermission'] = Relationship(
    #     back_populates='user', cascade_delete=True)
    # otps: list['OTP'] = Relationship(
    #     back_populates='user', cascade_delete=True)

    _ROUTER_TAG = 'User'

    # @property
    # def is_public(self) -> bool:
    #     return self.username is not None

    # def get_dir(self, root: pathlib.Path) -> pathlib.Path:
    #     if self.is_public:
    #         return root / self.username
    #     else:
    #         return root / self.id

    # @classmethod
    # async def authenticate(cls, session: Session, username_or_email: types.UserTypes.email | types.UserTypes.username, password: types.UserTypes.password) -> typing.Self | None:

    #     query = select(cls).where(
    #         or_(cls.email == username_or_email, cls.username == username_or_email))
    #     user = session.exec(query).one_or_none()

    #     if not user:
    #         return None
    #     if user.hashed_password is None:
    #         return None
    #     if not utils.verify_password(password, user.hashed_password):
    #         return None
    #     return user

    # @classmethod
    # @api_endpoint
    # async def is_username_available(cls, session: Session, username: types.UserTypes.username) -> bool:

    #     if session.exec(select(cls).where(User.username == username)).one_or_none():
    #         return False
    #     return True

    # @classmethod
    # async def api_get_is_username_available(cls, session: Session, username: types.UserTypes.username) -> None:
    #     if not await cls.is_username_available(session, username):
    #         raise HTTPException(
    #             status_code=status.HTTP_409_CONFLICT, detail='Username already exists')

    # @classmethod
    # async def is_email_available(cls, session: Session, email: types.UserTypes.email) -> bool:
    #     if session.exec(select(cls).where(User.email == email)).one_or_none():
    #         return False
    #     return True

    # @classmethod
    # @api_endpoint
    # async def api_get_is_email_available(cls, session: Session, email: types.UserTypes.email) -> None:
    #     if not await cls.is_email_available(session, email):
    #         raise HTTPException(
    #             status_code=status.HTTP_409_CONFLICT, detail='Email already exists')

    # @classmethod
    # def hash_password(cls, password: types.UserTypes.password) -> types.UserTypes.hashed_password:
    #     return utils.hash_password(password)

    # async def _check_authorization_existing(self, params):
    #     if not params.admin:
    #         if self._id != params.authorized_user_id:
    #             if self.is_public:
    #                 if params.method == 'delete' or params.method == 'patch':
    #                     raise HTTPException(
    #                         status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to {method} this user'.format(method=params.method))
    #             else:
    #                 raise self.not_found_exception()

    # @classmethod
    # async def _check_validation_post(cls, params):

    #     if 'username' in params.create_model.model_fields_set:
    #         if params.create_model.username != None:
    #             await User.api_get_is_username_available(
    #                 params.session, params.create_model.username)
    #     if 'email' in params.create_model.model_fields_set:
    #         if params.create_model.email != None:
    #             await User.api_get_is_email_available(params.session, params.create_model.email)

    # async def _check_validation_patch(self, params):
    #     if 'username' in params.update_model.model_fields_set:
    #         if params.update_model.username is not None:
    #             await User.api_get_is_username_available(
    #                 params.session, params.update_model.username)
    #     if 'email' in params.update_model.model_fields_set:
    #         if params.update_model.email is not None:
    #             await User.api_get_is_email_available(params.session, params.update_model.email)

    # @classmethod
    # async def create(cls, params) -> typing.Self:

    #     new_user = cls(
    #         id=cls.generate_id(),
    #         hashed_password=cls.hash_password(
    #             params.create_model.password) if 'password' in params.create_model.model_fields_set else None,
    #         **params.create_model.model_dump(exclude=['password'])
    #     )

    #     root_gallery = await Gallery.api_post(Gallery.PostParams(**params.model_dump(exclude=['create_model', 'create_method_params', 'authorized_user_id']), authorized_user_id=new_user._id, create_model=GalleryAdminCreate(
    #         name='root', user_id=new_user._id, visibility_level=config.VISIBILITY_LEVEL_NAME_MAPPING['private']
    #     )))

    #     return new_user

    # async def update(self, params):

    #     self.sqlmodel_update(params.update_model.model_dump(
    #         exclude_unset=True, exclude=['password']))
    #     if 'password' in params.update_model.model_fields_set:
    #         self.hashed_password = self.hash_password(
    #             params.update_model.password)

    #     # rename the root gallery if the username is updated
    #     if 'username' in params.update_model.model_fields_set:
    #         root_gallery = await Gallery.get_root_gallery(params.session, self._id)
    #         await root_gallery.update(
    #             Gallery.PatchParams(**params.model_dump(exclude=['update_model', 'update_method_params']),
    #                                 update_model=GalleryAdminUpdate(
    #                 name=self._id if self.username == None else self.username
    #             ))
    #         )

    # async def delete(self, params):
    #     await (await Gallery.get_root_gallery(params.session, self._id)).delete(session=params.session, c=params.c,
    #                                                                             authorized_user_id=params.authorized_user_id, admin=params.admin)


class UserExport(TableExport, UserIdBase):
    id: types.UserTypes.id
    username: typing.Optional[types.UserTypes.username]


class UserPublic(UserExport):
    pass


class UserPrivate(UserExport):
    email: types.UserTypes.email
    user_role_id: types.UserTypes.user_role_id


'''



# Define a custom SQLAlchemy type for string serialization
class DateTimeWithTimeZoneString(TypeDecorator):
    impl = String  # Underlying type in the database

    def process_bind_param(self, value: datetime_module.datetime, dialect) -> str:
        """Convert datetime to string before saving to the database."""
        if value is None:
            return None
        if isinstance(value, datetime_module.datetime):
            return value.isoformat()  # Serialize to ISO 8601 format
        raise ValueError("Value must be a datetime object")

    def process_result_value(self, value: str, dialect) -> datetime_module.datetime:
        """convert from string to datetime after loading from the database."""
        if value is None:
            return None
        return datetime_module.datetime.fromisoformat(value)


def validate_and_normalize_datetime(value: datetime_module.datetime, info: ValidationInfo) -> datetime_module.datetime:
    if value.tzinfo == None:
        raise ValueError(info.field_name + ' must have a timezone')
    return value.astimezone(datetime_module.timezone.utc)




def build_pagination[TQuery: Select](query: TQuery, pagination: Pagination):
    return query.offset(pagination.offset).limit(pagination.limit)


class OrderBy[T](BaseModel):
    field: T
    ascending: bool







# JWT


class JwtIO[TEncode: dict, TDecode: dict](BaseModel):

    _JWT_CLAIMS_MAPPING: typing.ClassVar[dict[str, str]] = {}

    @classmethod
    def validate_jwt_claims(cls, payload: TEncode) -> bool:
        return all(claim in payload for claim in cls._JWT_CLAIMS_MAPPING)

    @classmethod
    def decode(cls, payload: TEncode) -> TDecode:
        return {cls._JWT_CLAIMS_MAPPING[claim]: payload.get(claim) for claim in cls._JWT_CLAIMS_MAPPING}

    def encode(self) -> TEncode:
        return {key: getattr(self, value) for key, value in self._JWT_CLAIMS_MAPPING.items()}


class AuthCredentialTypes:
    issued = typing.Annotated[datetime_module.datetime,
                              'The datetime at which the auth credential was issued']
    issued_timestamp = typing.Annotated[float,
                                        'The datetime at which the auth credential was issued']
    expiry = typing.Annotated[datetime_module.datetime,
                              'The datetime at which the auth credential will expire']
    expiry_timestamp = typing.Annotated[float,
                                        'The datetime at which the auth credential will expire']
    lifespan = typing.Annotated[datetime_module.timedelta,
                                'The timedelta from creation in which the auth credential is still valid']
    type = typing.Literal['access_token', 'api_key', 'otp', 'sign_up']


class AuthCredential:

    class Import(BaseModel):
        lifespan: typing.Optional[AuthCredentialTypes.lifespan] = None
        expiry: typing.Optional[AuthCredentialTypes.expiry] = None

    class Create(Import):
        @model_validator(mode='after')
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

    class Update(Import):
        pass

    class JwtEncodeBase(typing.TypedDict):
        exp: AuthCredentialTypes.expiry_timestamp
        iat: AuthCredentialTypes.issued_timestamp
        type: AuthCredentialTypes.type

    class JwtDecodeBase(typing.TypedDict):
        expiry: AuthCredentialTypes.expiry_timestamp
        issued: AuthCredentialTypes.issued_timestamp
        type: AuthCredentialTypes.type

    class JwtIO[TEncode: dict, TDecode: dict](JwtIO[TEncode, TDecode]):
        _TYPE_CLAIM: typing.ClassVar[str] = 'type'

    class Model(JwtIO):

        # repeated in child classes due to behavior of sqlalchemy with custom type
        issued: AuthCredentialTypes.issued = Field(
            const=True, sa_column=Column(DateTimeWithTimeZoneString))
        expiry: AuthCredentialTypes.expiry = Field(
            sa_column=Column(DateTimeWithTimeZoneString))
        auth_type: typing.ClassVar[AuthCredentialTypes.type]

        _JWT_CLAIMS_MAPPING_BASE: typing.ClassVar[dict[str, str]] = {
            'exp': 'expiry',
            'iat': 'issued',
            'type': 'auth_type',
        }

        @field_validator('issued', 'expiry')
        @classmethod
        def validate_datetime(cls, value: datetime_module.datetime, info: ValidationInfo) -> datetime_module.datetime:
            return validate_and_normalize_datetime(value, info)

        @field_serializer('issued', 'expiry')
        def serialize_datetime(value: datetime_module.datetime) -> datetime_module.datetime:
            return value.replace(tzinfo=datetime_module.timezone.utc)

    class Table(Table):

        user_id: types.UserTypes.id = Field(
            index=True, foreign_key=User.__tablename__ + '.' + User._ID_COLS[0], const=True, ondelete='CASCADE')

        @classmethod
        async def create(cls, params: PostParams['AuthCredential.Create', BaseModel]) -> typing.Self:

            return cls(
                id=cls.generate_id(),
                issued=datetime_module.datetime.now(
                    datetime_module.timezone.utc),
                expiry=params.create_model.get_expiry(),
                **params.create_model.model_dump(exclude=['lifespan', 'expiry'])
            )

        @classmethod
        async def get_scope_ids(cls, session: Session = None) -> list[types.ScopeTypes.id]:
            return []


# UserAccessToken

class UserAccessTokenTypes(AuthCredentialTypes):
    id = str


class UserAccessTokenIdBase(IdObject[UserAccessTokenTypes.id]):
    id: UserAccessTokenTypes.id = Field(
        primary_key=True, index=True, unique=True, const=True)


class UserAccessTokenAdminUpdate(BaseModel):
    pass


class UserAccessTokenAdminCreate(AuthCredential.Create):
    user_id: types.UserTypes.id


class UserAccessTokenJwt:
    class Encode(AuthCredential.JwtEncodeBase):
        sub: types.UserTypes.id

    class Decode(AuthCredential.JwtDecodeBase):
        id: types.UserTypes.id


class UserAccessToken(
        Table['UserAccessToken', UserAccessTokenTypes.id, UserAccessTokenAdminCreate,
              BaseModel, BaseModel, UserAccessTokenAdminUpdate, BaseModel, BaseModel, typing.Literal[()]],
        AuthCredential.Table,
        AuthCredential.JwtIO[UserAccessTokenJwt.Encode,
                             UserAccessTokenJwt.Decode],
        AuthCredential.Model,
        UserAccessTokenIdBase,
        table=True):

    auth_type = 'access_token'
    __tablename__ = 'user_access_token'

    issued: AuthCredentialTypes.issued = Field(
        const=True, sa_column=Column(DateTimeWithTimeZoneString))
    expiry: AuthCredentialTypes.expiry = Field(
        sa_column=Column(DateTimeWithTimeZoneString))

    user: 'User' = Relationship(
        back_populates='user_access_tokens')

    _JWT_CLAIMS_MAPPING = {
        **AuthCredential.Model._JWT_CLAIMS_MAPPING_BASE, **{'sub': 'id'}}
    _ROUTER_TAG: typing.ClassVar[str] = 'User Access Token'

    @classmethod
    async def _check_authorization_post(cls, params):

        if not params.admin:
            if params.authorized_user_id != params.create_model.user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to post access token for another user')

    async def _check_authorization_existing(self, params):
        if not params.admin:
            if self.user_id != params.authorized_user_id:
                raise self.not_found_exception()

    async def get_scope_ids(self, session: Session = None) -> list[types.ScopeTypes.id]:
        return config.USER_ROLE_ID_SCOPE_IDS[self.user.user_role_id]


# OTP


class OTPConfig:
    CODE_LENGTH: typing.ClassVar[int] = 6


class OTPTypes(AuthCredentialTypes):
    id = str
    code = typing.Annotated[str, StringConstraints(
        min_length=OTPConfig.CODE_LENGTH, max_length=OTPConfig.CODE_LENGTH, pattern=re.compile(r'^\d{6}$'))]
    hashed_code = str


class OTPIdBase(IdObject[OTPTypes.id]):
    id: OTPTypes.id = Field(
        primary_key=True, index=True, unique=True, const=True)


class OTPAdminUpdate(BaseModel):
    pass


class OTPAdminCreate(AuthCredential.Create):
    user_id: types.UserTypes.id
    hashed_code: OTPTypes.hashed_code


class OTP(
        Table['OTP', OTPTypes.id,
              OTPAdminCreate, BaseModel, BaseModel, OTPAdminUpdate, BaseModel, BaseModel, typing.Literal[()]],
        AuthCredential.Table,
        AuthCredential.Model,
        OTPIdBase,
        table=True):

    auth_type = 'otp'
    __tablename__ = 'otp'

    issued: AuthCredentialTypes.issued = Field(
        const=True, sa_column=Column(DateTimeWithTimeZoneString))
    expiry: AuthCredentialTypes.expiry = Field(
        sa_column=Column(DateTimeWithTimeZoneString))

    hashed_code: OTPTypes.hashed_code = Field()
    user: 'User' = Relationship(
        back_populates='otps')

    _ROUTER_TAG = 'One Time Password'

    @classmethod
    def generate_code(cls) -> OTPTypes.code:
        characters = string.digits
        return ''.join(secrets.choice(characters) for _ in range(OTPConfig.CODE_LENGTH))

    @classmethod
    def hash_code(cls, code: OTPTypes.code) -> OTPTypes.hashed_code:
        return utils.hash_password(code)

    @classmethod
    def verify_code(cls, code: OTPTypes.code, hashed_code: OTPTypes.hashed_code) -> bool:

        import time
        start = time.time()
        a = utils.verify_password(code, hashed_code)
        end = time.time()
        print(end - start)
        return a


# ApiKey


class ApiKeyTypes(AuthCredentialTypes):
    id = str
    name = typing.Annotated[str, StringConstraints(
        min_length=1, max_length=256)]
    order_by = typing.Literal['issued', 'expiry', 'name']


class ApiKeyIdBase(IdObject[ApiKeyTypes.id]):
    id: ApiKeyTypes.id = Field(
        primary_key=True, index=True, unique=True, const=True)


class ApiKeyAvailable(BaseModel):
    name: ApiKeyTypes.name


class ApiKeyAdminAvailable(ApiKeyAvailable):
    user_id: types.UserTypes.id


class ApiKeyImport(AuthCredential.Import):
    pass


class ApiKeyUpdate(ApiKeyImport, AuthCredential.Update):
    name: typing.Optional[ApiKeyTypes.name] = None


class ApiKeyAdminUpdate(ApiKeyUpdate):
    pass


class ApiKeyCreate(ApiKeyImport, AuthCredential.Create):
    name: ApiKeyTypes.name


class ApiKeyAdminCreate(ApiKeyCreate):
    user_id: types.UserTypes.id


class ApiKeyJwt:
    class Encode(AuthCredential.JwtEncodeBase):
        sub: types.UserTypes.id

    class Decode(AuthCredential.JwtDecodeBase):
        id: types.UserTypes.id


class ApiKey(
        Table['ApiKey', ApiKeyTypes.id,
              ApiKeyAdminCreate, BaseModel, BaseModel,  ApiKeyAdminUpdate, BaseModel, BaseModel, ApiKeyTypes.order_by],
        AuthCredential.Table,
        AuthCredential.JwtIO[ApiKeyJwt.Encode, ApiKeyJwt.Decode],
        AuthCredential.Model,
        ApiKeyIdBase,
        table=True):
    auth_type = 'api_key'
    __tablename__ = 'api_key'

    issued: AuthCredentialTypes.issued = Field(
        const=True, sa_column=Column(DateTimeWithTimeZoneString))
    expiry: AuthCredentialTypes.expiry = Field(
        sa_column=Column(DateTimeWithTimeZoneString))

    name: ApiKeyTypes.name = Field()
    user: 'User' = Relationship(back_populates='api_keys')
    api_key_scopes: list['ApiKeyScope'] = Relationship(
        back_populates='api_key', cascade_delete=True)

    _JWT_CLAIMS_MAPPING = {
        **AuthCredential.Model._JWT_CLAIMS_MAPPING_BASE, **{'sub': 'id'}}

    _ROUTER_TAG = 'Api Key'

    async def get_scope_ids(self, session: Session = None, c: client.Client = None) -> list[types.ScopeTypes.id]:
        return [api_key_scope.scope_id for api_key_scope in self.api_key_scopes]

    @classmethod
    async def is_available(cls, session: Session, api_key_available_admin: ApiKeyAdminAvailable) -> bool:
        return not session.exec(select(cls).where(cls._build_conditions(api_key_available_admin.model_dump()))).one_or_none()

    @classmethod
    async def api_get_is_available(cls, session: Session, api_key_available_admin: ApiKeyAdminAvailable) -> None:

        if not await cls.is_available(session, api_key_available_admin):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=cls.already_exists_message())

    @classmethod
    async def _check_authorization_post(cls, params):
        if not params.admin:
            if params.authorized_user_id != params.create_model.user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to post api key for another user')

    async def _check_authorization_existing(self, params):
        if not params.admin:
            if self.user_id != params.authorized_user_id:
                raise self.not_found_exception()

    @classmethod
    async def _check_validation_post(cls, params):
        await cls.api_get_is_available(params.session, ApiKeyAdminAvailable(
            name=params.create_model.name, user_id=params.create_model.user_id)
        )

    async def _check_validation_patch(self, params):
        if 'name' in params.update_model.model_fields_set:
            await self.api_get_is_available(params.session, ApiKeyAdminAvailable(
                name=params.update_model.name, user_id=params.authorized_user_id))


class ApiKeyExport(TableExport):
    id: ApiKeyTypes.id
    user_id: types.UserTypes.id
    name: ApiKeyTypes.name
    issued: ApiKeyTypes.issued
    expiry: ApiKeyTypes.expiry


class ApiKeyPublic(ApiKeyExport):
    pass


class ApiKeyPrivate(ApiKeyExport):
    scope_ids: list[types.ScopeTypes.id]

    @classmethod
    def from_api_key(cls, api_key: ApiKey) -> typing.Self:
        return cls.model_construct(**api_key.model_dump(), scope_ids=[api_key_scope.scope_id for api_key_scope in api_key.api_key_scopes])


# SignUp


class SignUpJwt:
    class Encode(AuthCredential.JwtEncodeBase):
        sub: types.UserTypes.email

    class Decode(AuthCredential.JwtDecodeBase):
        email: types.UserTypes.email


class SignUpAdminCreate(AuthCredential.Create):
    email: types.UserTypes.email


class SignUp(
    AuthCredential.JwtIO[SignUpJwt.Encode, SignUpJwt.Decode],
    AuthCredential.Model,
):
    auth_type = 'sign_up'
    email: types.UserTypes.email = Field()
    issued: AuthCredentialTypes.issued = Field(
        const=True, sa_column=Column(DateTimeWithTimeZoneString))
    expiry: AuthCredentialTypes.expiry = Field(
        sa_column=Column(DateTimeWithTimeZoneString))

    _JWT_CLAIMS_MAPPING = {
        **AuthCredential.Model._JWT_CLAIMS_MAPPING_BASE, **{'sub': 'email'}}

    @classmethod
    def create(cls, create_model: SignUpAdminCreate) -> typing.Self:
        return cls(
            issued=datetime_module.datetime.now(
                datetime_module.timezone.utc),
            expiry=create_model.get_expiry(),
            **create_model.model_dump(exclude=['lifespan', 'expiry'])
        )


AuthCredentialClass = UserAccessToken | ApiKey | OTP | SignUp
AuthCredentialId = UserAccessTokenTypes.id | ApiKeyTypes.id | OTPTypes.id


AUTH_CREDENTIAL_CLASSES: set[AuthCredentialClass] = {
    UserAccessToken, ApiKey, OTP, SignUp}

AuthCredentialTokenType = typing.Literal['access_token', 'api_key', 'sign_up']
AuthCredentialTokenClass = UserAccessToken | ApiKey | SignUp
AUTH_CREDENTIAL_TOKEN_CLASSES: set[AuthCredentialTokenClass] = {
    UserAccessToken, ApiKey, SignUp}

AuthCredentialTableClass = UserAccessToken | ApiKey | OTP
AUTH_CREDENTIAL_TABLE_CLASSES: set[AuthCredentialTableClass] = {
    UserAccessToken, ApiKey, OTP}

AUTH_CREDENTIAL_TYPE_TO_CLASS: dict[AuthCredentialTypes.type, AuthCredentialClass] = {
    'access_token': UserAccessToken,
    'api_key': ApiKey,
    'otp': OTP,
    'sign_up': SignUp
}


class ApiKeyScopeTypes:
    id = typing.Annotated[tuple[ApiKeyTypes.id,
                                types.ScopeTypes.id], '(api_key_id, scope_id)'
                          ]


class ApiKeyScopeIdBase(IdObject[ApiKeyScopeTypes.id]):
    _ID_COLS: typing.ClassVar[list[str]] = ['api_key_id', 'scope_id']

    api_key_id: ApiKeyTypes.id = Field(
        index=True, foreign_key=ApiKey.__tablename__ + '.' + ApiKey._ID_COLS[0], ondelete='CASCADE')
    scope_id: types.ScopeTypes.id = Field(index=True)


class ApiKeyScopeAdminUpdate(BaseModel):
    pass


class ApiKeyScopeAdminCreate(ApiKeyScopeIdBase):
    pass


class ApiKeyScope(
        Table['ApiKeyScope', ApiKeyScopeTypes.id,
              ApiKeyScopeAdminCreate, BaseModel, BaseModel, ApiKeyScopeAdminUpdate, BaseModel, BaseModel, typing.Literal[()]],
        ApiKeyScopeIdBase,
        table=True):

    __tablename__ = 'api_key_scope'
    __table_args__ = (
        PrimaryKeyConstraint('api_key_id', 'scope_id'),
    )

    api_key: ApiKey = Relationship(
        back_populates='api_key_scopes')

    _ROUTER_TAG: typing.ClassVar[str] = 'Api Key Scope'

    @classmethod
    async def create(cls, params):
        return ApiKeyScope(
            **params.create_model.model_dump(),
        )

    @classmethod
    async def _check_authorization_post(cls, params):
        api_key = await ApiKey.read(params.session, params.create_model.api_key_id)
        if not api_key:
            raise ApiKey.not_found_exception()

        if not params.admin:
            if api_key.user_id != params.authorized_user_id:
                raise cls.not_found_exception()

    @classmethod
    async def _check_validation_post(cls, params):
        if await cls.read(params.session, params.create_model._id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail='Api key scope already exists')

    async def _check_authorization_existing(self, params):
        if not params.admin:
            if self.api_key.user_id != params.authorized_user_id:
                raise self.not_found_exception()


class GalleryTypes:
    class BaseTypes:
        id = str

    id = BaseTypes.id
    user_id = types.UserTypes.id

    # name can't start with the `YYYY-MM-DD ` pattern
    name = typing.Annotated[str, StringConstraints(
        min_length=1, max_length=256, pattern=re.compile(r'^(?!\d{4}-\d{2}-\d{2} ).*'))]
    visibility_level = types.VisibilityLevelTypes.id
    parent_id = BaseTypes.id
    description = typing.Annotated[str, StringConstraints(
        min_length=0, max_length=20000)]
    date = datetime_module.date
    folder_name = str


class GalleryIdBase(IdObject[GalleryTypes.id]):
    id: GalleryTypes.id = Field(
        primary_key=True, index=True, unique=True, const=True)


class GalleryExport(TableExport):
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


class GalleryImport(BaseModel):
    pass


class GalleryUpdate(GalleryImport):
    name: typing.Optional[GalleryTypes.name] = None
    user_id: typing.Optional[GalleryTypes.user_id] = None
    visibility_level: typing.Optional[GalleryTypes.visibility_level] = None
    parent_id: typing.Optional[GalleryTypes.parent_id] = None
    description: typing.Optional[GalleryTypes.description] = None
    date: typing.Optional[GalleryTypes.date] = None


class GalleryAdminUpdate(GalleryUpdate):
    pass


class GalleryAdminUpdateParams(BaseModel):
    pass


class GalleryCreate(GalleryImport):
    name: GalleryTypes.name
    visibility_level: GalleryTypes.visibility_level
    parent_id: GalleryTypes.parent_id
    description: typing.Optional[GalleryTypes.description] = None
    date: typing.Optional[GalleryTypes.date] = None


class GalleryAdminCreate(GalleryCreate):
    user_id: GalleryTypes.user_id
    parent_id: typing.Optional[GalleryTypes.parent_id] = None


class GalleryAdminCreateParams(BaseModel):
    mkdir: bool = True


class GalleryAvailable(BaseModel):
    name: GalleryTypes.name
    parent_id: typing.Optional[GalleryTypes.parent_id] = None
    date: typing.Optional[GalleryTypes.date] = None


class GalleryAdminAvailable(GalleryAvailable):
    user_id: types.UserTypes.id


class GalleryAdminDeleteParams(BaseModel):
    rmtree: bool = True


class Gallery(
        Table['Gallery', GalleryTypes.id, GalleryAdminCreate, GalleryAdminCreateParams,
              BaseModel, GalleryAdminUpdate, GalleryAdminUpdateParams, GalleryAdminDeleteParams, typing.Literal[()]],
        GalleryIdBase,
        table=True):
    __tablename__ = 'gallery'

    name: GalleryTypes.name = Field()
    user_id: GalleryTypes.user_id = Field(
        index=True, foreign_key=User.__tablename__ + '.' + User._ID_COLS[0], ondelete='CASCADE')

    visibility_level: GalleryTypes.visibility_level = Field()
    parent_id: GalleryTypes.parent_id = Field(nullable=True, index=True,
                                              foreign_key=__tablename__ + '.id', ondelete='CASCADE')
    description: GalleryTypes.description = Field(nullable=True)
    date: GalleryTypes.date = Field(nullable=True)

    user: 'User' = Relationship(back_populates='galleries')
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

    _ROUTER_TAG: typing.ClassVar[str] = 'Gallery'

    @property
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
            a = await (await self.read(session, self.parent_id)).get_dir(session, root)
            return a / self.folder_name

    async def get_parents(self, session: Session) -> list[typing.Self]:

        if self.parent_id is None:
            return []
        else:
            return (await self.parent.get_parents(session)) + [self.parent]

    @classmethod
    async def get_root_gallery(cls, session: Session, user_id: GalleryTypes.user_id) -> typing.Self | None:
        return session.exec(select(cls).where(cls.user_id == user_id).where(cls.parent_id == None)).one_or_none()

    @classmethod
    async def api_get_is_available(cls, session: Session, gallery_available_admin: GalleryAdminAvailable) -> None:

        # raise an exception if the parent gallery does not exist
        if gallery_available_admin.parent_id:
            if not await cls.read(session, gallery_available_admin.parent_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail='Parent gallery does not exist')

        if session.exec(select(cls).where(cls._build_conditions(gallery_available_admin.model_dump()))).one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=cls.already_exists_message())

    @classmethod
    async def _check_authorization_post(cls, params):
        if not params.admin:
            if params.authorized_user_id != params.create_model.user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to post gallery for another user')

    async def _check_authorization_existing(self, params):

        if not params.admin:
            if params.authorized_user_id != self.user_id:

                if params.method == 'delete':
                    raise HTTPException(
                        status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to {method} this gallery'.format(method=params.method))

                gallery_permission = await GalleryPermission.read(params.session, (params.id, params.authorized_user_id))

                # if the gallery is private and user has no access, pretend it doesn't exist
                if not gallery_permission and self.visibility_level == config.VISIBILITY_LEVEL_NAME_MAPPING['private']:
                    raise self.not_found_exception()

                elif params.method == 'get':
                    if gallery_permission.permission_level < config.PERMISSION_LEVEL_NAME_MAPPING['viewer']:
                        raise HTTPException(
                            status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to {method} this gallery'.format(method=params.method))

                elif params.method == 'patch':
                    if gallery_permission.permission_level < config.PERMISSION_LEVEL_NAME_MAPPING['editor']:
                        raise HTTPException(
                            status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to {method} this gallery'.format(method=params.method))

    @classmethod
    async def _check_validation_post(cls, params):
        await cls.api_get_is_available(params.session, GalleryAdminAvailable(**params.create_model.model_dump(include=GalleryAdminAvailable.model_fields.keys(), exclude_unset=True)))

    async def _check_validation_patch(self, params):
        # take self, overwrite it with the update_model, and see if the combined model is available
        await self.api_get_is_available(params.session, GalleryAdminAvailable(**{
            **self.model_dump(include=list(GalleryAdminAvailable.model_fields.keys())), **params.update_model.model_dump(include=GalleryAdminAvailable.model_fields.keys(), exclude_unset=True)
        }))

    @classmethod
    async def create(cls, params):
        gallery = cls(
            id=cls.generate_id(),
            **params.create_model.model_dump()
        )

        if params.create_method_params == None:
            params.create_method_params = GalleryAdminCreateParams()

        if params.create_method_params.mkdir:
            (await gallery.get_dir(params.session, params.c.galleries_dir)).mkdir()

        return gallery

    async def update(self, params) -> None:

        rename_folder = False

        # rename the folder
        if 'name' in params.update_model.model_fields_set or 'date' in params.update_model.model_fields_set or 'parent_id' in params.update_model.model_fields_set:
            rename_folder = True
            original_dir = await self.get_dir(
                params.session, params.c.galleries_dir)

        self.sqlmodel_update(
            params.update_model.model_dump(exclude_unset=True))

        if rename_folder:
            new_dir = (await self.get_dir(params.session, params.c.galleries_dir)).parent / self.folder_name
            original_dir.rename(new_dir)

    async def delete(self, params) -> None:

        if params.delete_method_params == None:
            params.delete_method_params = GalleryAdminCreateParams()

        if params.delete_method_params.rmtree:
            shutil.rmtree((await self.get_dir(params.session, params.c.galleries_dir)))

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
            await Gallery.api_delete(session=session, c=c, id=gallery._id, authorized_user_id=self.user_id, admin=False, delete_method_kwargs=GalleryAdminDeleteParams(rmtree=False))

        for folder_name in to_add:
            date, name = self.get_date_and_name_from_folder_name(
                folder_name)
            new_gallery = await Gallery.api_post(
                session=session, c=c, authorized_user_id=self.user_id, admin=False, create_model=GalleryAdminCreate(name=name, user_id=self.user_id, visibility_level=self.visibility_level, parent_id=self.id, date=date),
                create_method_kwargs=GalleryAdminCreateParams(mkdir=False))

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
            if file.suffix in ImageFileMetadataConfig._SUFFIXES:
                image_version = await ImageVersion.read(session, file.image_file_metadata.version_id)
                if len(image_version.image_file_metadatas) == 1:
                    await ImageVersion.api_delete(session=session, c=c, id=image_version.id, authorized_user_id=self.user_id, admin=False)

            await File.api_delete(session=session, c=c, id=file.id, authorized_user_id=self.user_id, admin=False, unlink=False)

        image_files: list[File] = []

        for file_name in to_add:
            stem = local_file_by_names[file_name].stem
            suffix = ''.join(suffixes) if (
                suffixes := local_file_by_names[file_name].suffixes) else None

            new_file = await File.api_post(
                session=session, c=c, authorized_user_id=self.user_id, admin=False, create_model=FileAdminCreate(stem=stem, suffix=suffix, gallery_id=self.id, size=local_file_by_names[file_name].stat().st_size))

            # rename the file, just to make sure the suffix is lowercase
            local_file_by_names[file_name].rename(
                local_file_by_names[file_name].with_name(new_file.name))

            if suffix in ImageFileMetadataConfig._SUFFIXES:
                image_files.append(new_file)

        # loop through files twice, adding the original images first
        for original_images in [True, False]:
            for image_file in image_files:

                base_name, version, scale = ImageFileMetadata.parse_file_stem(
                    image_file.stem)

                if original_images == (version == None):

                    parent_id = None
                    if version is not None:
                        image_version_og = session.exec(select(ImageVersion).where(ImageVersion.gallery_id == self._id).where(
                            ImageVersion.base_name == base_name).where(ImageVersion.version == None)).one_or_none()

                        # if an original exists, assume the version wants to link as the parent
                        if image_version_og:
                            parent_id = image_version_og._id

                    image_version_kwargs = {
                        'gallery_id': self.id,
                        'base_name': base_name if parent_id is None else None,
                        'version': version,
                        'parent_id': parent_id
                    }

                    image_version = session.exec(select(ImageVersion).where(
                        ImageVersion._build_conditions(image_version_kwargs))).one_or_none()

                    # this if the first file of this version
                    if not image_version:
                        image_version = await ImageVersion.api_post(session=session, c=c, authorized_user_id=self.user_id, admin=False, create_model=ImageVersionAdminCreate(**image_version_kwargs))

                    image_file_metadata = await ImageFileMetadata.api_post(session=session, c=c, authorized_user_id=self.user_id, admin=False, create_model=ImageFileMetadataAdminCreate(file_id=image_file.id, version_id=image_version.id, scale=scale))

        # recursively sync children
        for child in self.children:
            await child.sync_with_local(session, c, dir / child.folder_name)


class GalleryPermissionTypes:
    class BaseTypes:
        gallery_id = GalleryTypes.id
        user_id = types.UserTypes.id

    id = typing.Annotated[tuple[BaseTypes.gallery_id,
                                BaseTypes.user_id], '(gallery_id, user_id)']
    gallery_id = BaseTypes.gallery_id
    user_id = BaseTypes.user_id
    permission_level = types.PermissionLevelTypes.id


class GalleryPermissionIdBase(IdObject[GalleryPermissionTypes.id]):
    _ID_COLS: typing.ClassVar[list[str]] = ['gallery_id', 'user_id']

    gallery_id: GalleryPermissionTypes.gallery_id = Field(
        primary_key=True, index=True, foreign_key=Gallery.__tablename__ + '.' + Gallery._ID_COLS[0], ondelete='CASCADE')
    user_id: GalleryPermissionTypes.user_id = Field(
        primary_key=True, index=True, foreign_key=User.__tablename__ + '.' + User._ID_COLS[0], ondelete='CASCADE')


class GalleryPermissionExport(TableExport):
    gallery_id: GalleryPermissionTypes.gallery_id
    user_id: GalleryPermissionTypes.user_id
    permission_level: GalleryPermissionTypes.permission_level


class GalleryPermissionPublic(GalleryPermissionExport):
    pass


class GalleryPermissionPrivate(GalleryPermissionExport):
    pass


class GalleryPermissionImport(BaseModel):
    pass


class GalleryPermissionAdminUpdate(GalleryPermissionImport):
    permission_level: typing.Optional[GalleryPermissionTypes.permission_level] = None


class GalleryPermissionAdminCreate(GalleryPermissionImport, GalleryPermissionIdBase):
    permission_level: GalleryPermissionTypes.permission_level


class GalleryPermission(
        Table['GalleryPermission',
              GalleryPermissionTypes.id, GalleryPermissionAdminCreate,  BaseModel, BaseModel, GalleryPermissionAdminUpdate, BaseModel, BaseModel, typing.Literal[()]],
        GalleryPermissionIdBase,
        table=True):
    __tablename__ = 'gallery_permission'
    __table_args__ = (
        PrimaryKeyConstraint('gallery_id', 'user_id'),
    )

    permission_level: GalleryPermissionTypes.permission_level = Field()

    gallery: 'Gallery' = Relationship(
        back_populates='gallery_permissions')
    user: 'User' = Relationship(
        back_populates='gallery_permissions')

    @classmethod
    async def _check_authorization_post(cls, params):

        if not params.admin:
            if not params.authorized_user_id == params.create_model.user_id:
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to post gallery permission for another user')

    @classmethod
    async def _check_validation_post(cls, params):
        if await GalleryPermission.read(params.session, params.create_model._id):
            raise HTTPException(
                status.HTTP_409_CONFLICT, detail='Gallery permission already exists')

    @classmethod
    async def create(cls, params):
        return cls(
            params.create_model.model_dump()
        )

    async def _check_authorization_existing(self, params):

        if not params.admin:
            if self.gallery.user._id != params.authorized_user_id:
                authorized_user_gallery_permission = await self.read(params.session, GalleryPermissionIdBase(
                    gallery_id=self.gallery._id, user_id=params.authorized_user_id
                )._id)

                if not authorized_user_gallery_permission:
                    raise self.not_found_exception()

                if params.method == 'delete' or params.method == 'patch':
                    raise HTTPException(
                        status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to {} this gallery permission'.format(params.method))


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


class FileExport(TableExport):
    id: FileTypes.id
    stem: FileTypes.stem
    suffix: FileTypes.suffix | None
    size: FileTypes.size


class FileImport(BaseModel):
    pass


class FileUpdate(FileImport):
    stem: typing.Optional[FileTypes.stem] = None
    gallery_id: typing.Optional[FileTypes.gallery_id] = None


class FileAdminUpdate(FileUpdate):
    pass


class FileCreate(FileImport):
    stem: FileTypes.stem
    suffix: FileTypes.suffix | None
    gallery_id: FileTypes.gallery_id
    size: FileTypes.size | None


class FileAdminCreate(FileCreate):
    pass


class File(
        Table['File', FileTypes.id, FileAdminCreate, BaseModel, BaseModel,
              FileAdminUpdate,  BaseModel, BaseModel, typing.Literal[()]],
        FileIdBase,
        table=True):

    __tablename__ = 'file'

    stem: FileTypes.stem = Field()
    suffix: FileTypes.suffix = Field(nullable=True)
    gallery_id: FileTypes.gallery_id = Field(
        index=True, foreign_key=Gallery.__tablename__ + '.' + Gallery._ID_COLS[0], ondelete='CASCADE')
    size: FileTypes.size = Field(nullable=True)

    gallery: Gallery = Relationship(back_populates='files')
    image_file_metadata: typing.Optional['ImageFileMetadata'] = Relationship(
        back_populates='file', cascade_delete=True)

    @property
    def name(self) -> str:
        return self.stem + ('' if self.suffix is None else self.suffix)


class ImageVersionTypes:

    class BaseTypes:
        id = str

    id = BaseTypes.id
    gallery_id = GalleryTypes.id
    base_name = typing.Annotated[str, StringConstraints(
        # prohibit underscore
        min_length=1, max_length=240, pattern=re.compile(r'^(?!.*_).+$')
    )]
    version = typing.Annotated[str, StringConstraints(
        # version cannot be exactly two digits
        pattern=re.compile(r'^(?!\d{2}$).+$'))]
    parent_id = BaseTypes.id
    datetime = datetime_module.datetime
    description = typing.Annotated[str, StringConstraints(
        min_length=0, max_length=20000)]
    aspect_ratio = float
    average_color = str


class ImageVersionIdBase(IdObject[ImageVersionTypes.id]):
    id: ImageVersionTypes.id = Field(
        primary_key=True, index=True, unique=True, const=True)


class ImageVersionExport(TableExport):
    id: ImageVersionTypes.id
    base_name: ImageVersionTypes.base_name | None
    parent_id: ImageVersionTypes.parent_id | None
    version: ImageVersionTypes.version | None
    datetime: ImageVersionTypes.datetime | None
    description: ImageVersionTypes.description | None
    aspect_ratio: ImageVersionTypes.aspect_ratio | None
    average_color: ImageVersionTypes.average_color | None


class ImageVersionImport(BaseModel):
    base_name: typing.Optional[ImageVersionTypes.base_name] = None
    parent_id: typing.Optional[ImageVersionTypes.parent_id] = None
    version: typing.Optional[ImageVersionTypes.version] = None
    datetime: typing.Optional[ImageVersionTypes.datetime] = None
    description: typing.Optional[ImageVersionTypes.description] = None


class ImageVersionUpdate(ImageVersionImport, ImageVersionIdBase):
    pass


class ImageVersionAdminUpdate(ImageVersionUpdate):
    pass


class ImageVersionCreate (ImageVersionImport):
    pass


class ImageVersionAdminCreate(ImageVersionCreate):
    gallery_id: ImageVersionTypes.gallery_id
    base_name: typing.Optional[ImageVersionTypes.base_name] = None
    version: typing.Optional[ImageVersionTypes.version] = None
    parent_id: typing.Optional[ImageVersionTypes.parent_id] = None
    datetime: typing.Optional[ImageVersionTypes.datetime] = None
    description: typing.Optional[ImageVersionTypes.description] = None
    aspect_ratio: typing.Optional[ImageVersionTypes.aspect_ratio] = None
    average_color: typing.Optional[ImageVersionTypes.average_color] = None


class ImageVersion(
        Table['ImageVersion', ImageVersionTypes.id,
              ImageVersionAdminCreate,  BaseModel, BaseModel, ImageVersionAdminUpdate, BaseModel, BaseModel, typing.Literal[()]],
        ImageVersionIdBase,
        table=True):
    __tablename__ = 'image_version'

    base_name: ImageVersionTypes.base_name = Field(
        nullable=True, index=True)
    parent_id: ImageVersionTypes.parent_id = Field(
        nullable=True, index=True, foreign_key=__tablename__ + '.id', ondelete='SET NULL')

    # BW, Edit1, etc. Original version is null
    version: ImageVersionTypes.version = Field(nullable=True)
    gallery_id: ImageVersionTypes.gallery_id = Field(
        index=True, foreign_key=Gallery.__tablename__ + '.' + Gallery._ID_COLS[0], ondelete='CASCADE')
    datetime: ImageVersionTypes.datetime = Field(nullable=True)
    description: ImageVersionTypes.description = Field(nullable=True)
    aspect_ratio: ImageVersionTypes.aspect_ratio = Field(nullable=True)
    average_color: ImageVersionTypes.average_color = Field(
        nullable=True)

    parent: typing.Optional['ImageVersion'] = Relationship(
        back_populates='children', sa_relationship_kwargs={'remote_side': 'ImageVersion.id'})
    children: list['ImageVersion'] = Relationship(
        back_populates='parent')

    image_file_metadatas: list['ImageFileMetadata'] = Relationship(
        back_populates='version')
    gallery: 'Gallery' = Relationship(
        back_populates='image_versions')

    @model_validator(mode='after')
    def validate_model(self, info: ValidationInfo) -> None:
        if self.base_name is None and self.parent_id is None:
            raise ValueError('Unnamed versions must have a parent_id')

    @field_validator('datetime')
    @classmethod
    def validate_datetime(cls, value: datetime_module.datetime, info: ValidationInfo) -> datetime_module.datetime:
        return validate_and_normalize_datetime(value, info)

    @field_serializer('datetime')
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


class ImageFileMetadataConfig:
    _SUFFIXES: typing.ClassVar[set[str]] = {
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}


class ImageFileMetadataTypes:
    file_id = FileTypes.id
    version_id = ImageVersionTypes.id
    scale = int


class ImageFileMetadataIdBase(IdObject[ImageFileMetadataTypes.file_id]):
    _ID_COLS: typing.ClassVar[list[str]] = ['file_id']

    file_id: ImageFileMetadataTypes.file_id = Field(
        primary_key=True, index=True, unique=True, const=True, foreign_key=File.__tablename__ + '.' + File._ID_COLS[0], ondelete='CASCADE')


class ImageFileMetadataExport(TableExport):
    file_id: ImageFileMetadataTypes.file_id
    version_id: ImageFileMetadataTypes.version_id
    scale: ImageFileMetadataTypes.scale | None


class ImageFileMetadataImport(BaseModel):
    pass


class ImageFileMetadataUpdate(ImageFileMetadataImport, ImageFileMetadataIdBase):
    pass


class ImageFileMetadataAdminUpdate(ImageFileMetadataUpdate):
    pass


class ImageFileMetadataCreate(ImageFileMetadataImport):
    file_id: ImageFileMetadataTypes.file_id
    version_id: ImageFileMetadataTypes.version_id
    scale: typing.Optional[ImageFileMetadataTypes.scale] = Field(
        default=None, ge=1, le=99)


class ImageFileMetadataAdminCreate(ImageFileMetadataCreate):
    pass


class ImageFileMetadata(
        Table['ImageFileMetadata', ImageFileMetadataTypes.file_id,
              ImageFileMetadataAdminCreate, BaseModel, BaseModel, ImageFileMetadataAdminUpdate, BaseModel, BaseModel, typing.Literal[()]],
        ImageFileMetadataIdBase,
        table=True):
    __tablename__ = 'image_file_metadata'

    version_id: ImageFileMetadataTypes.version_id = Field(
        index=True, foreign_key=ImageVersion.__tablename__ + '.' + ImageVersion._ID_COLS[0], ondelete='CASCADE')
    scale: ImageFileMetadataTypes.scale = Field(
        nullable=True, ge=1, le=99)

    version: 'ImageVersion' = Relationship(
        back_populates='image_file_metadatas')
    file: 'File' = Relationship(
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

    @classmethod
    async def create(cls, params):
        return cls(
            params.create_model.model_dump()
        )

'''
