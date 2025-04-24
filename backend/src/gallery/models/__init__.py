from sqlmodel import SQLModel
from typing import Type, Protocol, TypeVar, Generic
from .. import types

from .tables import User, UserAccessToken, OTP, ApiKey, ApiKeyScope, Gallery, GalleryPermission, File, ImageVersion, ImageFileMetadata


Table = User | UserAccessToken | OTP | ApiKey | ApiKeyScope | Gallery | GalleryPermission | File | ImageVersion | ImageFileMetadata
TableSimple = User | UserAccessToken | OTP | ApiKey | Gallery | File | ImageVersion

TTable = TypeVar('TTable', bound=Table)
TTable_co = TypeVar('TTable_co', bound=Table, covariant=True)
TTable_contra = TypeVar('TTable_contra', bound=Table, contravariant=True)

TTableSimple = TypeVar('TTableSimple', bound=TableSimple)
TTableSimpleId_co = TypeVar(
    'TTableSimpleId_co', bound=TableSimple, covariant=True)
TTableSimpleId_contra = TypeVar(
    'TTableSimpleId_contra', bound=TableSimple, contravariant=True)


class HasTable(Protocol[TTable_co]):
    _TABLE: Type[TTable_co]
