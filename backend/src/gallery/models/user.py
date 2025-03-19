from sqlmodel import Field, Relationship, select, SQLModel
from typing import TYPE_CHECKING, TypedDict, Optional
from gallery.models.bases.table import Table as BaseTable
from gallery.models.bases.router import Router as BaseRouter
from gallery import types, client
from pydantic import BaseModel
from fastapi import APIRouter

if TYPE_CHECKING:
    pass

ID_COL = 'id'


class Id(SQLModel):
    id: types.ImageVersion.id = Field(
        primary_key=True, index=True, unique=True, const=True)


class Import(BaseModel):
    phone_number: Optional[types.User.phone_number] = None
    username: Optional[types.User.username] = None
    password: Optional[types.User.password] = None


class Update(Import):
    email: Optional[types.User.email] = None


class AdminUpdate(Update):
    user_role_id: Optional[types.User.user_role_id] = None


class Create(Import):
    email: types.User.email


class AdminCreate(Create):
    user_role_id: types.User.user_role_id


class Export(Id):
    username: Optional[types.User.username]


class Public(Export):
    pass


class Private(Export):
    email: types.User.email
    user_role_id: types.User.user_role_id


class User(BaseTable['User', Id], Id, table=True):

    id: types.User.id = Field(primary_key=True, index=True, unique=True)
    email: types.User.email = Field(index=True, unique=True, nullable=False)
    phone_number: types.User.phone_number | None = Field(
        index=True, unique=True, nullable=True)
    username: types.User.username | None = Field(
        index=True, unique=True, nullable=True)
    hashed_password: types.User.hashed_password | None = Field(nullable=False)
    user_role_id: types.User.user_role_id = Field(nullable=False)

    @classmethod
    def _build_get_by_id_query(cls, id: Id):
        return select(cls).where(cls.id == id.id)


class Router(BaseRouter):

    _PREFIX = '/user'
    _TAGS = ['User']

    def _set_routes(self):

        @self.router.get("/{user_id}", response_model=Public)
        async def get_user_by_id(user_id: types.User.id):
            async with self.client.AsyncSession() as session:
                return Public(id='1', username='test')


'''


class UserDB(BaseDB):
    __tablename__ = "user"

    id: Mapped[str] = mapped_column(primary_key=True, index=True, unique=True)
    email: Mapped[str] = mapped_column(index=True, unique=True, nullable=False)
    phone_number: Mapped[str | None] = mapped_column(unique=True)
    username: Mapped[str | None] = mapped_column(index=True, unique=True)
    hashed_password: Mapped[str | None] = mapped_column()
    user_role_id: Mapped[int] = mapped_column(nullable=False)

    @property
    def is_public(self) -> bool:
        return self.username is not None

    def get_dir(self, root: pathlib.Path) -> pathlib.Path:
        if self.is_public:
            # since username is not None, it is a string (linter)
            return root / str(self.username)
        else:
            return root / self.id


class UserIdBase(IdObject[types.User.id]):
    id: types.User.id


class UserImport(BaseModel):
    phone_number: typing.Optional[types.User.phone_number] = None
    username: typing.Optional[types.User.username] = None
    password: typing.Optional[types.User.password] = None


class UserUpdate(UserImport):
    email: typing.Optional[types.User.email] = None


class UserAdminUpdate(UserUpdate):
    user_role_id: typing.Optional[types.User.user_role_id] = None


class UserCCreate(UserImport):
    email: types.User.email


class UserAdminCreate(UserCCreate):
    user_role_id: types.User.user_role_id


class Test2(Test):
    test2: str


class User(TableService[UserDB, types.User.id, UserAdminCreate, UserAdminUpdate, Test2, typing.Literal[()]]):

    # api_keys: list['ApiKey'] = Relationship(
    #     back_populates='user', cascadedelete=True)
    # user_access_tokens: list['UserAccessToken'] = Relationship(
    #     back_populates='user', cascadedelete=True)
    # galleries: list['Gallery'] = Relationship(
    #     back_populates='user', cascadedelete=True)
    # gallery_permissions: list['GalleryPermission'] = Relationship(
    #     back_populates='user', cascadedelete=True)
    # otps: list['OTP'] = Relationship(
    #     back_populates='user', cascadedelete=True)

    _ROUTER_TAG = 'User'
    BASE_DB = UserDB

    @classmethod
    async def authenticate(cls, session: AsyncSession, username_or_email: types.User.email | types.User.username, password: types.User.password) -> typing.Self | None:

        query: Select[UserDB] = select(UserDB).where(or_(
            UserDB.email == username_or_email, UserDB.username == username_or_email))
        user: UserDB = (await session.execute(query)).scalar_one_or_none()

        if not user:
            return None
        if user.hashed_password is None:
            return None
        if not utils.verify_password(password, user.hashed_password):
            return None
        return user

    @classmethod
    async def api_get(cls, params, **kwargs):

        reveal_type(params)
        reveal_type(kwargs)

    @classmethod
    async def is_username_available(cls, session: AsyncSession, username: types.User.username) -> bool:

        query: Select[UserDB] = select(UserDB).where(
            UserDB.username == username)
        return not (await session.execute(query)).scalar_one_or_none()

    @classmethod
    async def api_get_is_username_available(cls, session: AsyncSession, username: types.User.username) -> None:
        if not await cls.is_username_available(session, username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail='Username already exists')

    @classmethod
    async def is_email_available(cls, session: AsyncSession, email: types.User.email) -> bool:

        query: Select[UserDB] = select(UserDB).where(UserDB.email == email)
        return not (await session.execute(query)).scalar_one_or_none()

    @classmethod
    async def api_get_is_email_available(cls, session: AsyncSession, email: types.User.email) -> None:
        if not await cls.is_email_available(session, email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail='Email already exists')

    @classmethod
    def hash_password(cls, password: types.User.password) -> types.User.hashed_password:
        return utils.hash_password(password)

    @classmethod
    async def _check_authorization_existing(cls, **kwargs):
        if not kwargs.get('admin'):
            if kwargs['inst']._id != kwargs.get('authorized_user_id'):
                if kwargs['inst'].is_public:
                    if kwargs['method'] == 'delete' or kwargs['method'] == 'patch':
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to {method} this user'.format(method=kwargs['method']))
                else:
                    raise cls.not_found_exception()

    @classmethod
    async def _check_validation_post(cls, **kwargs):

        if 'username' in kwargs['cCreate_model'].model_fields_set:
            if kwargs['cCreate_model'].username is not None:
                await User.api_get_is_username_available(
                    kwargs['session'], kwargs['cCreate_model'].username)
        if 'email' in kwargs['cCreate_model'].model_fields_set:
            if kwargs['cCreate_model'].email is not None:
                await User.api_get_is_email_available(kwargs['session'], kwargs['cCreate_model'].email)

    @classmethod
    async def _check_validation_patch(cls, **kwargs):
        if 'username' in kwargs['update_model'].model_fields_set:
            if kwargs['update_model'].username is not None:
                await User.api_get_is_username_available(
                    kwargs['session'], kwargs['update_model'].username)
        if 'email' in kwargs['update_model'].model_fields_set:
            if kwargs['update_model'].email is not None:
                await User.api_get_is_email_available(kwargs['session'], kwargs['update_model'].email)

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
        #                             update_model=GalleryAdminUpdate(
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
