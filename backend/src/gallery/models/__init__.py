from sqlmodel import SQLModel
from typing import Type, Protocol, TypeVar, Generic
from .. import types

from .tables import User, UserAccessToken, OTP, ApiKey, ApiKeyScope, Gallery, GalleryPermission, File, ImageVersion, ImageFileMetadata
from .models import SignUp

Model = User | UserAccessToken | OTP | ApiKey | ApiKeyScope | Gallery | GalleryPermission | File | ImageVersion | ImageFileMetadata | SignUp
ModelSimple = User | UserAccessToken | OTP | ApiKey | Gallery | File | ImageVersion

TModel = TypeVar('TModel', bound=Model)
TModel_co = TypeVar('TModel_co', bound=Model, covariant=True)
TModel_contra = TypeVar('TModel_contra', bound=Model, contravariant=True)

TModelSimple = TypeVar('TModelSimple', bound=ModelSimple)
TModelSimple_co = TypeVar(
    'TModelSimple_co', bound=ModelSimple, covariant=True)
TModelSimple_contra = TypeVar(
    'TModelSimple_contra', bound=ModelSimple, contravariant=True)


class HasSimpleId(Protocol[types.TIdSimple]):
    id: types.TIdSimple
