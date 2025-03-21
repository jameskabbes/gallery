from sqlmodel import Field, Relationship, select, SQLModel
from typing import TYPE_CHECKING, TypedDict, Optional, Self, NotRequired

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, or_
from fastapi import HTTPException, status

from gallery.models.bases import table, router
from gallery import types, client, utils
from pydantic import BaseModel
import pathlib

if TYPE_CHECKING:
    from gallery.models import user, gallery, api_key, user_access_token, gallery_permission, otp

ID_COL = 'id'


class UserId(SQLModel):
    id: types.ImageVersion.id = Field(
        primary_key=True, index=True, unique=True, const=True)


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


class UserExport(UserId):
    username: Optional[types.User.username]


class UserPublic(UserExport):
    pass


class UserPrivate(UserExport):
    email: types.User.email
    user_role_id: types.User.user_role_id


class User(table.Table[UserId, UserAdminCreate, UserAdminUpdate], UserId, table=True):

    __tablename__ = 'user'  # type: ignore

    id: types.User.id = Field(primary_key=True, index=True, unique=True)
    email: types.User.email = Field(index=True, unique=True, nullable=False)
    phone_number: types.User.phone_number | None = Field(
        index=True, unique=True, nullable=True)
    username: types.User.username | None = Field(
        index=True, unique=True, nullable=True)
    hashed_password: types.User.hashed_password | None = Field(nullable=False)
    user_role_id: types.User.user_role_id = Field(nullable=False)

    api_keys: list['api_key.ApiKey'] = Relationship(
        back_populates='user', cascade_delete=True)
    user_access_tokens: list['user_access_token.UserAccessToken'] = Relationship(
        back_populates='user', cascade_delete=True)
    galleries: list['gallery.Gallery'] = Relationship(
        back_populates='user', cascade_delete=True)
    gallery_permissions: list['gallery_permission.GalleryPermission'] = Relationship(
        back_populates='user', cascade_delete=True)
    otps: list['otp.OTP'] = Relationship(
        back_populates='user', cascade_delete=True)

    @property
    def is_public(self) -> bool:
        return self.username is not None

    def get_dir(self, root: pathlib.Path) -> pathlib.Path:
        if self.is_public:
            # since username is not None, it is a string (linter)
            return root / str(self.username)
        else:
            return root / self.id

    @classmethod
    def _build_select_by_id(cls, id: UserId):
        return select(User).where(User.id == id)

    @classmethod
    async def authenticate(cls, session: AsyncSession, username_or_email: types.User.email | types.User.username, password: types.User.password) -> Self | None:

        query = select(cls).where(
            or_(cls.username == username_or_email, cls.email == username_or_email))
        user = (await session.exec(query)).one_or_none()

        if not user:
            return None
        if user.hashed_password is None:
            return None
        if not utils.verify_password(password, user.hashed_password):
            return None
        return user

    @classmethod
    async def is_username_available(cls, session: AsyncSession, username: types.User.username) -> bool:

        query = select(cls).where(cls.username == username)
        return (await session.exec(query)).one_or_none() is not None

    # @classmethod
    # async def api_get_is_username_available(cls, session: AsyncSession, username: types.User.username) -> None:
    #     if not await cls.is_username_available(session, username):
    #         raise HTTPException(
    #             status_code=status.HTTP_409_CONFLICT, detail='Username already exists')

    @classmethod
    async def is_email_available(cls, session: AsyncSession, email: types.User.email) -> bool:

        query = select(cls).where(cls.email == email)
        return (await session.exec(query)).one_or_none() is not None

    # @classmethod
    # async def get_is_email_available(cls, session: AsyncSession, email: types.User.email) -> None:
    #     if not await cls.is_email_available(session, email):
    #         raise HTTPException(
    #             status_code=status.HTTP_409_CONFLICT, detail='Email already exists')

    @classmethod
    def hash_password(cls, password: types.User.password) -> types.User.hashed_password:
        return utils.hash_password(password)

    # @classmethod
    # async def _check_authorization_existing(cls, **kwargs):
    #     if not kwargs.get('admin'):
    #         if kwargs['inst']._id != kwargs.get('authorized_user_id'):
    #             if kwargs['inst'].is_public:
    #                 if kwargs['method'] == 'delete' or kwargs['method'] == 'patch':
    #                     raise HTTPException(
    #                         status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to {method} this user'.format(method=kwargs['method']))
    #             else:
    #                 raise cls.not_found_exception()

    # @classmethod
    # async def _check_validation_post(cls, **kwargs):

    #     if 'username' in kwargs['cCreate_model'].model_fields_set:
    #         if kwargs['cCreate_model'].username is not None:
    #             await User.api_get_is_username_available(
    #                 kwargs['session'], kwargs['cCreate_model'].username)
    #     if 'email' in kwargs['cCreate_model'].model_fields_set:
    #         if kwargs['cCreate_model'].email is not None:
    #             await User.api_get_is_email_available(kwargs['session'], kwargs['cCreate_model'].email)

    # @classmethod
    # async def _check_validation_patch(cls, **kwargs):
    #     if 'username' in kwargs['update_model'].model_fields_set:
    #         if kwargs['update_model'].username is not None:
    #             await User.api_get_is_username_available(
    #                 kwargs['session'], kwargs['update_model'].username)
    #     if 'email' in kwargs['update_model'].model_fields_set:
    #         if kwargs['update_model'].email is not None:
    #             await User.api_get_is_email_available(kwargs['session'], kwargs['update_model'].email)


class UserRouter(router.Router):

    _PREFIX = '/user'
    _TAGS = ['User']

    def _set_routes(self):

        @self.router.get("/{user_id}", response_model=UserPublic)
        async def get_user_by_id(user_id: types.User.id):
            async with self.client.AsyncSession() as session:
                return UserPublic(id=user_id, username='test')


'''





    @classmethod
    async def db_inst_from_add_model(cls, **kwargs):
        return UserDB(
            id=UserDB.generate_id(),
            hashed_password=cls.hash_password(
                kwargs['cCreate_model'].password) if 'password' in kwargs['cCreate_model'].model_fields_set else None,
            **kwargs['cCreate_model'].model_dump(exclude=['password'])
        )

    @classmethod
    async def api_post_custom(cls, **kwargs):
        pass
        # root_gallery = await Gallery.api_post(Gallery.ApiPostParams(**params.model_dump(exclude=['cCreate_model', 'cCreate_method_params', 'authorized_user_id']), authorized_user_id=new_user._id, cCreate_model=GalleryAdminCreate(
        #     name='root', user_id=new_user._id, visibility_level=config.VISIBILITY_LEVEL_NAME_MAPPING['private']
        # )))

    @classmethod
    async def update_db_inst_from_update_model(cls, db_inst, **kwargs):
        for key, value in kwargs['update_model'].model_dump(exclude_unset=True, exclude={'password'}).items():
            setattr(db_inst, key, value)

        if 'password' in kwargs['update_model'].model_fields_set:
            db_inst.hashed_password = cls.hash_password(
                kwargs['update_model'].password)

    @classmethod
    async def api_patch_custom(cls, test=None, **kwargs):
        # rename the root gallery if the username is updated
        # if 'username' in params.update_model.model_fields_set:
        #     root_gallery = await Gallery.get_root_gallery(params.session, self._id)
        #     await root_gallery.update(
        #         Gallery.ApiGetParams(**params.model_dump(exclude=['update_model', 'update_method_params']),
        #                             update_model=GalleryAdminUserUpdate(
        #             name=self._id if self.username == None else self.username
        #         ))
        #     )

        pass

    @classmethod
    async def api_delete_custom(cls, **kwargs):
        pass
        # await (await Gallery.get_root_gallery(params.session, self._id)).delete(session=params.session, c=params.c,
        #                                                                         authorized_user_id=params.authorized_user_id, admin=params.admin)




'''
