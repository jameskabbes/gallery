from sqlmodel import select
from ..models.tables import GalleryPermission as GalleryPermissionTable
from . import base
from .. import types

from ..schemas import gallery_permission as gallery_permission_schema


class GalleryPermission(
    base.Service[
        GalleryPermissionTable,
        types.GalleryPermission.id,
        gallery_permission_schema.GalleryPermissionAdminCreate,
        gallery_permission_schema.GalleryPermissionAdminUpdate,
    ],
        table=True):

    _TABLE = GalleryPermissionTable

    @classmethod
    def table_id(cls, inst):
        return types.GalleryPermissionId(
            gallery_id=inst.gallery_id,
            user_id=inst.user_id,
        )

    @classmethod
    def _build_select_by_id(cls, id):
        return select(cls._TABLE).where(cls._TABLE.gallery_id == id.gallery_id, cls._TABLE.user_id == id.user_id)

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
