from fastapi import Depends, status, UploadFile, HTTPException
from sqlmodel import select
from ..models.tables import Gallery as GalleryTable, GalleryPermission as GalleryPermissionTable
from ..services.gallery import Gallery as GalleryService
from ..services.gallery_permission import GalleryPermission as GalleryPermissionService
from ..schemas import gallery as gallery_schema, pagination as pagination_schema, api as api_schema, gallery_permission as gallery_permission_schema
from ..routers import user as user_router
from . import base
from .. import types
from typing import Annotated, cast
from ..auth import utils as auth_utils
from ..config import settings
import shutil


class _Base(
    base.Router[
        GalleryTable,
        types.User.id,
        gallery_schema.GalleryAdminCreate,
        gallery_schema.GalleryAdminUpdate,
    ],
):
    _PREFIX = '/galleries'
    _TAG = 'Gallery'
    _SERVICE = GalleryService


galleries_pagination = base.get_pagination()


# class UploadFileToGalleryResponse(BaseModel):
#     message: str


class GalleryRouter(_Base):
    _ADMIN = False

    def _set_routes(self):

        # @self.router.get('/', tags=[user_router._Base._TAG])
        # async def get_galleries(
        #     authorization: Annotated[auth_utils.GetAuthReturn, Depends(
        #         auth_utils.make_get_auth_dependency(c=self.client))],
        #     pagination: pagination_schema.Pagination = Depends(
        #         galleries_pagination)

        # ) -> list[gallery_schema.GalleryPrivate]:

        #     return [gallery_schema.GalleryPrivate.model_validate(gallery) for gallery in
        #             await self.get_many({
        #                 'authorization': authorization,
        #                 'c': self.client,
        #                 'pagination': pagination,
        #                 'query': select(GalleryTable).where(GalleryTable.user_id == authorization._user_id)
        #             })
        #             ]

        @self.router.get('/{gallery_id}/')
        async def get_gallery_by_id(
            gallery_id: types.Gallery.id,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(c=self.client, raise_exceptions=False))]
        ) -> gallery_schema.GalleryPublic:

            return gallery_schema.GalleryPublic.model_validate(await self.get({
                'authorization': authorization,
                'c': self.client,
                'id': gallery_id,
            }))

        @self.router.post('/')
        async def post_gallery(
            gallery_create: gallery_schema.GalleryCreate,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(c=self.client))]
        ) -> gallery_schema.GalleryPrivate:

            return gallery_schema.GalleryPrivate.model_validate(await self.post({
                'authorization': authorization,
                'c': self.client,
                'create_model': gallery_schema.GalleryAdminCreate(
                    **gallery_create.model_dump(exclude_unset=True), user_id=cast(types.User.id, authorization._user_id)),
            }))

        @self.router.patch('/{gallery_id}/')
        async def patch_gallery(
            gallery_id: types.Gallery.id,
            gallery_update: gallery_schema.GalleryUpdate,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(c=self.client, ))]
        ) -> gallery_schema.GalleryPrivate:

            return gallery_schema.GalleryPrivate.model_validate(await self.patch({
                'authorization': authorization,
                'c': self.client,
                'id': gallery_id,
                'update_model': gallery_schema.GalleryAdminUpdate(
                    **gallery_update.model_dump(exclude_unset=True)),
            }))

        @self.router.delete('/{gallery_id}/', status_code=status.HTTP_204_NO_CONTENT)
        async def delete_gallery(
            gallery_id: types.Gallery.id,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(c=self.client, ))]
        ):

            return await self.delete({
                'authorization': authorization,
                'c': self.client,
                'id': gallery_id,
            })

        @self.router.get('/details/available/')
        async def get_gallery_available(
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(c=self.client, ))],
            gallery_available: gallery_schema.GalleryAvailable = Depends(),
        ):

            async with self.client.AsyncSession() as session:

                return api_schema.IsAvailableResponse(
                    available=await GalleryService.is_available(
                        session=session,
                        gallery_available_admin=gallery_schema.GalleryAdminAvailable(
                            **gallery_available.model_dump(exclude_unset=True),
                            user_id=cast(types.User.id, authorization._user_id)
                        )

                    )
                )

        # need to decide how to deal with gallery permissions and how to return

        # @self.router.get('/users/{user_id}/', tags=[models.User._ROUTER_TAG])
        # async def get_galleries_by_user(
        #     user_id: models.UserTypes.id,
        #     authorization: Annotated[auth_utils.GetAuthReturn, Depends(
        #         get_auth_from_token(raise_exceptions=False))],
        #     pagination: PaginationParams = Depends(get_pagination_params),
        # ) -> list[models.GalleryPublic]:

        #     async with c.AsyncSession() as session:
        #         galleries = session.exec(select(models.Gallery).where(
        #             models.Gallery.user_id == user_id).offset(pagination.offset).limit(pagination.limit)).all()
        #         return [models.GalleryPublic.model_validate(gallery) for gallery in galleries]

        @self.router.post("/{gallery_id}/upload/", status_code=status.HTTP_201_CREATED)
        async def upload_file_to_gallery(
            gallery_id: types.Gallery.id,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(c=self.client))],
            file: UploadFile
        ):

            async with self.client.AsyncSession() as session:

                gallery = await GalleryService.fetch_by_id(session, gallery_id)
                if not gallery:
                    raise base.NotFoundError(GalleryTable, gallery_id)

                if gallery.user.id != authorization._user_id:
                    gallery_permission = await GalleryPermissionService.fetch_by_id(
                        session, types.GalleryPermission.id(
                            gallery_id, cast(types.User.id, authorization._user_id))
                    )

                    if gallery_permission is None:
                        if gallery.visibility_level == settings.VISIBILITY_LEVEL_NAME_MAPPING['private']:
                            raise base.NotFoundError(GalleryTable, gallery_id)

                        if gallery.visibility_level == settings.VISIBILITY_LEVEL_NAME_MAPPING['public']:
                            raise HTTPException(
                                status.HTTP_403_FORBIDDEN, detail='User lacks edit permission for this gallery')
                    else:
                        if gallery_permission.permission_level < settings.PERMISSION_LEVEL_NAME_MAPPING['editor']:
                            raise HTTPException(
                                status.HTTP_403_FORBIDDEN, detail='User does not have permission to add files to this gallery')

                file_path = (await GalleryService.get_dir(session, gallery, self.client.galleries_dir)).joinpath(file.filename or 'test.jpg')
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)


class GalleryAdminRouter(_Base):
    _ADMIN = True

    def _set_routes(self):

        @self.router.get('/{gallery_id}/')
        async def get_gallery_by_id_admin(
            gallery_id: types.Gallery.id,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(c=self.client, required_scopes={'admin'}))]
        ) -> GalleryTable:
            return await self.get({
                'authorization': authorization,
                'c': self.client,
                'id': gallery_id,
            })

        @self.router.post('/')
        async def post_gallery_admin(
            gallery_create_admin: gallery_schema.GalleryAdminCreate,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(c=self.client, required_scopes={'admin'}))]
        ) -> GalleryTable:
            return await self.post({
                'authorization': authorization,
                'c': self.client,
                'create_model': gallery_create_admin
            })

        @self.router.patch('/{gallery_id}/')
        async def patch_gallery_admin(
            gallery_id: types.Gallery.id,
            gallery_update_admin: gallery_schema.GalleryAdminUpdate,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(c=self.client, required_scopes={'admin'}))]
        ) -> GalleryTable:

            return await self.patch({
                'authorization': authorization,
                'c': self.client,
                'id': gallery_id,
                'update_model': gallery_update_admin
            })

        @self.router.delete('/{gallery_id}/', status_code=status.HTTP_204_NO_CONTENT)
        async def delete_gallery_admin(
            gallery_id: types.Gallery.id,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(c=self.client, required_scopes={'admin'}))]
        ):

            return await self.delete({
                'authorization': authorization,
                'c': self.client,
                'id': gallery_id,
            })

        @self.router.get('/details/available/')
        async def get_gallery_available_admin(
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(c=self.client, required_scopes={'admin'}))],
            gallery_available_admin: gallery_schema.GalleryAdminAvailable = Depends(),
        ):

            async with self.client.AsyncSession() as session:
                return api_schema.IsAvailableResponse(
                    available=await GalleryService.is_available(
                        session=session,
                        gallery_available_admin=gallery_schema.GalleryAdminAvailable(
                            **gallery_available_admin.model_dump(exclude_unset=True),
                            user_id=cast(types.User.id, authorization._user_id)
                        )
                    )
                )

        # add user tag
        @self.router.get('/users/{user_id}')
        async def get_galleries_by_user_admin(
            user_id: types.User.id,
            authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency(c=self.client, required_scopes={'admin'}))],
            pagination: pagination_schema.Pagination = Depends(
                galleries_pagination)
        ) -> list[GalleryTable]:

            return list(await self.get_many({
                'authorization': authorization,
                'c': self.client,
                'query': select(GalleryTable).where(
                    GalleryTable.user_id == user_id),
                'pagination': pagination
            }))

        # @self.router.post('/{gallery_id}/sync/')
        # async def sync_gallery(
        #     gallery_id: types.Gallery.id,
        #     authorization: Annotated[auth_utils.GetAuthReturn, Depends(
        #         auth_utils.make_get_auth_dependency(c=self.client, ))]
        # ) -> api_schema.DetailOnlyResponse:

        #     async with self.client.AsyncSession() as session:
        #         gallery = await GalleryTable.api_get(GalleryTable.GetParams.model_construct(session=session, c=c, authorized_user_id=authorization._user_id, id=gallery_id))
        #         dir = await gallery.get_dir(session, c.galleries_dir)
        #         await gallery.sync_with_local(session, c, dir)
        #         return api_schema.DetailOnlyResponse(detail='Synced gallery')
