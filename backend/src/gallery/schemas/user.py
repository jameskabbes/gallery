from pydantic import BaseModel, Field
from typing import Optional
from .. import types
from ..schemas import FromAttributes


class UserImport(BaseModel):
    phone_number: Optional[types.User.phone_number] = None
    username: Optional[types.User.username] = None
    password: Optional[types.User.password] = None


class UserUpdate(UserImport):
    email: Optional[types.User.email] = None


class UserAdminUpdate(UserUpdate):
    user_role_id: Optional[types.User.user_role_id] = None


class UserCreate(UserImport):
    email: types.User.email


class UserAdminCreate(UserCreate):
    user_role_id: types.User.user_role_id


class UserExport(FromAttributes):
    id: types.User.id
    username: Optional[types.User.username] = None


class UserPublic(UserExport):
    pass


class UserPrivate(UserExport):
    email: types.User.email
    user_role_id: types.User.user_role_id
