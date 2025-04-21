from sqlmodel import Field, Relationship, SQLModel
from pydantic import BaseModel, model_validator, field_serializer, field_validator, ValidationInfo
from . import types
from typing import ClassVar
from sqlmodel import Column
import datetime as datetime_module
from .custom_field_types import timestamp
from ..schemas import auth as auth_schemas


class User(SQLModel, table=True):

    __tablename__ = 'user'  # type: ignore

    id: types.User.id = Field(
        primary_key=True, index=True, unique=True, const=True)
    email: types.User.email = Field(index=True, unique=True, nullable=False)
    phone_number: types.User.phone_number | None = Field(
        index=True, unique=True, nullable=True)
    username: types.User.username | None = Field(
        index=True, unique=True, nullable=True)
    hashed_password: types.User.hashed_password | None = Field(nullable=False)
    user_role_id: types.User.user_role_id = Field(nullable=False)

    api_keys: list['ApiKey'] = Relationship(
        back_populates='user', cascade_delete=True)
    user_access_tokens: list['UserAccessToken'] = Relationship(
        back_populates='user', cascade_delete=True)
    galleries: list['Gallery'] = Relationship(
        back_populates='user', cascade_delete=True)
    gallery_permissions: list['GalleryPermission'] = Relationship(
        back_populates='user', cascade_delete=True)
    otp: 'OTP' = Relationship(
        back_populates='user', cascade_delete=True)


class _AuthCredentialModel(auth_schemas.AuthCredential):

    issued: types.AuthCredential.issued = Field(
        const=True, sa_column=Column(timestamp.Timestamp))
    expiry: types.AuthCredential.expiry = Field(
        sa_column=Column(timestamp.Timestamp))

    user_id: types.User.id = Field(
        index=True, foreign_key=str(User.__tablename__) + '.' + User.id, const=True, ondelete='CASCADE')


class UserAccessToken(SQLModel, _AuthCredentialModel, table=True):

    __tablename__ = 'user_access_token'  # type: ignore

    id: types.ImageVersion.id = Field(
        primary_key=True, index=True, unique=True, const=True)
    user: 'User' = Relationship(back_populates='user_access_tokens')


class OTP(SQLModel, _AuthCredentialModel, table=True):

    __tablename__ = 'otp'  # type: ignore

    auth_type = 'otp'

    id: types.OTP.id = Field(
        primary_key=True, index=False, unique=True, const=True)
    hashed_code: types.OTP.hashed_code = Field()
    user: 'User' = Relationship(
        back_populates='otp')


class ApiKey(SQLModel, _AuthCredentialWithUserId, table=True):

    __tablename__ = 'api_key'  # type: ignore

    id: types.ApiKey.id = Field(
        primary_key=True, index=True, unique=True, const=True)
    name: types.ApiKey.name = Field()
    user: 'User' = Relationship(back_populates='api_keys')
    api_key_scopes: list['ApiKeyScope'] = Relationship(
        back_populates='api_key', cascade_delete=True)
