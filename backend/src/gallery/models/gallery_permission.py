from sqlmodel import Field, Relationship, select, SQLModel
from typing import TYPE_CHECKING, TypedDict, Optional, ClassVar
from gallery.models.bases.table import Table as BaseTable
from gallery import types
from pydantic import BaseModel
from sqlalchemy.ext.declarative import declared_attr

from gallery.models import user, gallery


class GalleryPermissionId(SQLModel):
    gallery_id: types.GalleryPermission.gallery_id = Field(
        primary_key=True, index=True, foreign_key=str(gallery.Gallery.__tablename__) + '.' + gallery.ID_COL, ondelete='CASCADE')
    user_id: types.GalleryPermission.user_id = Field(
        primary_key=True, index=True, foreign_key=str(user.User.__tablename__) + '.' + user.ID_COL, ondelete='CASCADE')


class GalleryExport(BaseModel):
    gallery_id: types.GalleryPermission.gallery_id
    user_id: types.GalleryPermission.user_id
    permission_level: types.GalleryPermission.permission_level


class Public(GalleryExport):
    pass


class Private(GalleryExport):
    pass


class GalleryPermissionImport(BaseModel):
    pass


class GalleryPermissionAdminUpdate(GalleryPermissionImport):
    permission_level: Optional[types.GalleryPermission.permission_level] = None


class GalleryPermissionAdminCreate(GalleryPermissionImport):
    gallery_id: types.GalleryPermission.gallery_id
    user_id: types.GalleryPermission.user_id
    permission_level: types.GalleryPermission.permission_level


class GalleryPermission(
        BaseTable[
            GalleryPermissionId, GalleryPermissionAdminCreate, GalleryPermissionAdminUpdate],
        GalleryPermissionId,
        table=True):

    __tablename__ = 'gallery_permission'  # type: ignore

    # __table_args__ = (
    #     PrimaryKeyConstraint('gallery_id', 'user_id'),
    # )

    permission_level: types.GalleryPermission.permission_level = Field()

    gallery: 'gallery.Gallery' = Relationship(
        back_populates='gallery_permissions')
    user: 'user.User' = Relationship(
        back_populates='gallery_permissions')

    # @classmethod
    # async def _check_authorization_new(cls, params):

    #     if not params.admin:
    #         if not params.authorized_user_id == params.create_model.user_id:
    #             raise HTTPException(
    #                 status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to post gallery permission for another user')

    # @classmethod
    # async def _check_validation_post(cls, params):
    #     if await GalleryPermission.read(params.session, params.create_model._id):
    #         raise HTTPException(
    #             status.HTTP_409_CONFLICT, detail='Gallery permission already exists')

    # @classmethod
    # async def create(cls, params):
    #     return cls(
    #         params.create_model.model_dump()
    #     )

    # async def _check_authorization_existing(self, params):

    #     if not params.admin:
    #         if self.gallery.user._id != params.authorized_user_id:
    #             authorized_user_gallery_permission = await self.read(params.session, GalleryPermissionGalleryPermissionIdBase(
    #                 gallery_id=self.gallery._id, user_id=params.authorized_user_id
    #             )._id)

    #             if not authorized_user_gallery_permission:
    #                 raise self.not_found_exception()

    #             if params.method == 'delete' or params.method == 'patch':
    #                 raise HTTPException(
    #                     status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to {} this gallery permission'.format(params.method))


'''
class GalleryPermissionTypes:
    class BaseTypes:
        gallery_id = GalleryTypes.id
        user_id = types.User.id

    id = typing.Annotated[tuple[BaseTypes.gallery_id,
                                BaseTypes.user_id], '(gallery_id, user_id)']
    gallery_id = BaseTypes.gallery_id
    user_id = BaseTypes.user_id
    permission_level = types.PermissionLevelTypes.id


class GalleryPermissionGalleryPermissionIdBase(GalleryPermissionIdObject[GalleryPermissionTypes.id]):
    ID_COLS: typing.ClassVar[list[str]] = ['gallery_id', 'user_id']

    gallery_id: GalleryPermissionTypes.gallery_id = Field(
        primary_key=True, index=True, foreign_key=Gallery.__tablename__ + '.' + Gallery.ID_COLS[0], ondelete='CASCADE')
    user_id: GalleryPermissionTypes.user_id = Field(
        primary_key=True, index=True, foreign_key=User.__tablename__ + '.' + User.ID_COLS[0], ondelete='CASCADE')


class GalleryPermissionGalleryExport(TableGalleryExport):
    gallery_id: GalleryPermissionTypes.gallery_id
    user_id: GalleryPermissionTypes.user_id
    permission_level: GalleryPermissionTypes.permission_level


class GalleryPermissionPublic(GalleryPermissionGalleryExport):
    pass


class GalleryPermissionPrivate(GalleryPermissionGalleryExport):
    pass


class GalleryPermissionGalleryPermissionImport(BaseModel):
    pass


class GalleryPermissionAdminUpdate(GalleryPermissionGalleryPermissionImport):
    permission_level: typing.Optional[GalleryPermissionTypes.permission_level] = None


class GalleryPermissionGalleryPermissionAdminCreate(GalleryPermissionGalleryPermissionImport, GalleryPermissionGalleryPermissionIdBase):
    permission_level: GalleryPermissionTypes.permission_level


class GalleryPermission(
        Table['GalleryPermission',
              GalleryPermissionTypes.id, GalleryPermissionGalleryPermissionAdminCreate,  BaseModel, BaseModel, GalleryPermissionAdminUpdate, BaseModel, BaseModel, typing.Literal[()]],
        GalleryPermissionGalleryPermissionIdBase,
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
    async def _check_authorization_new(cls, params):

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
                authorized_user_gallery_permission = await self.read(params.session, GalleryPermissionGalleryPermissionIdBase(
                    gallery_id=self.gallery._id, user_id=params.authorized_user_id
                )._id)

                if not authorized_user_gallery_permission:
                    raise self.not_found_exception()

                if params.method == 'delete' or params.method == 'patch':
                    raise HTTPException(
                        status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to {} this gallery permission'.format(params.method))

'''
