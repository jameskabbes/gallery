from fastapi import Depends, status
from sqlmodel import select, func
from pydantic import BaseModel
from collections.abc import Sequence
from typing import Annotated, cast

from src.gallery import types
from src.gallery.routers import user as user_router, api_key as api_key_router, gallery as gallery_router, base
from src.gallery.schemas import api_key as api_key_schema, pagination as pagination_schema, api as api_schema, order_by as order_by_schema, user as user_schema, user_access_token as user_access_token_schema, gallery as gallery_schema
from src.gallery.models.tables import ApiKey as ApiKeyTable, UserAccessToken as UserAccessTokenTable
from src.gallery.services.api_key import ApiKey as ApiKeyService
from src.gallery.auth import utils as auth_utils


class GetProfilePageResponse(auth_utils.GetUserSessionInfoNestedReturn):
    user: user_schema.UserPrivate | None = None


class GetHomePageResponse(auth_utils.GetUserSessionInfoNestedReturn):
    pass


class GetSettingsPageResponse(auth_utils.GetUserSessionInfoNestedReturn):
    pass


class GetSettingsApiKeysPageResponse(auth_utils.GetUserSessionInfoNestedReturn):
    api_key_count: int
    api_keys: list[api_key_schema.ApiKeyPrivate]


class GetSettingsUserAccessTokensPageResponse(auth_utils.GetUserSessionInfoNestedReturn):
    user_access_token_count: int
    user_access_tokens: list[UserAccessTokenTable]


class GetStylesPageResponse(auth_utils.GetUserSessionInfoNestedReturn):
    pass


class GetGalleryPageResponse(auth_utils.GetUserSessionInfoNestedReturn):
    gallery: gallery_schema.GalleryPublic
    parents: list[gallery_schema.GalleryPublic]
    children: list[gallery_schema.GalleryPublic]


class _Base(base.Router):
    _PREFIX = '/pages'
    _TAG = 'Page'


class PagesRouter(_Base):
    _ADMIN = False

    def _set_routes(self):
        @self.router.get('/profile/', tags=[user_router._Base._TAG])
        async def get_pages_profile(authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                auth_utils.make_get_auth_dependency())]) -> GetProfilePageResponse:

            return GetProfilePageResponse(
                **auth_utils.get_user_session_info(authorization).model_dump()
            )

        @self.router.get('/home/')
        async def get_home_page(authorization: Annotated[auth_utils.GetAuthReturn, Depends(auth_utils.make_get_auth_dependency(raise_exceptions=False))]) -> GetHomePageResponse:
            return GetHomePageResponse(
                **auth_utils.get_user_session_info(authorization).model_dump()
            )

        @self.router.get('/settings/')
        async def get_settings_page(
                authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                    auth_utils.make_get_auth_dependency(raise_exceptions=False))]
        ) -> GetSettingsPageResponse:
            return GetSettingsPageResponse(
                **auth_utils.get_user_session_info(authorization).model_dump()
            )

        # @self.router.get('/settings/api-keys/', tags=[api_key_router._Base._TAG])
        # async def get_settings_api_keys_page(
        #     authorization: Annotated[auth_utils.GetAuthReturn, Depends(auth_utils.make_get_auth_dependency())],
        #     pagination: pagination_schema.Pagination = Depends(
        #         api_key_router.api_key_pagination),
        #     order_by: order_by_schema.OrderBy[types.ApiKey.order_by] = Depends(api_key_router.ApiKeyRouter.order_by_depends
        #                                                                        ),

        # ) -> GetSettingsApiKeysPageResponse:
        #     return GetSettingsApiKeysPageResponse(
        #         **auth_utils.get_user_session_info(authorization).model_dump(),
        #         api_key_count=await api_key_router.ApiKeyRouter(authorization),
        #         api_keys=await get_user_api_keys(authorization, get_api_keys_query_params)
        #     )

        # @self.router.get('/settings/user-access-tokens/', tags=[tables.UserAccessToken._ROUTER_TAG])
        # async def get_settings_user_access_tokens_page(
        #     authorization: Annotated[auth_utils.GetAuthReturn, Depends(auth_utils.make_get_auth_dependency())],
        #     pagination: tables.Pagination = Depends(
        #         user_access_token_pagination)
        # ) -> GetSettingsUserAccessTokensPageResponse:
        #     return GetSettingsUserAccessTokensPageResponse(
        #         **auth_utils.get_user_session_info(authorization).model_dump()
        #         user_access_token_count=await get_user_access_tokens_count(authorization),
        #         user_access_tokens=await get_user_access_tokens(authorization, pagination)
        #     )

        # @self.router.get('/styles/')
        # async def get_styles_page(authorization: Annotated[auth_utils.GetAuthReturn, Depends(auth_utils.make_get_auth_dependency(raise_exceptions=False))]) -> GetStylesPageResponse:
        #     return GetStylesPageResponse(
        #         **auth_utils.get_user_session_info(authorization).model_dump()
        #     )

        # @self.router.get('/galleries/{gallery_id}/', responses={status.HTTP_404_NOT_FOUND: {"description": tables.Gallery.not_found_message(), 'model': NotFoundResponse}}, tags=[tables.Gallery._ROUTER_TAG])
        # async def get_gallery_page(
        #     gallery_id: tables.GalleryTypes.id,
        #     authorization: Annotated[auth_utils.GetAuthReturn, Depends(
        #         auth_utils.make_get_auth_dependency(raise_exceptions=False))],
        #     root: bool = Query(False),
        # ) -> GetGalleryPageResponse:

        #     async with c.AsyncSession() as session:
        #         if root:
        #             if not authorization.isAuthorized:
        #                 raise tables.Gallery.not_found_exception()

        #             gallery = await tables.Gallery.get_root_gallery(session, authorization._user_id)
        #             gallery_id = gallery._id

        #         else:
        #             gallery = await tables.Gallery.api_get(tables.Gallery.GetParams.model_construct(
        #                 session=session, c=c,  authorized_user_id=authorization._user_id, id=gallery_id
        #             ))

        #         return GetGalleryPageResponse(
        #             **get_auth(authorization).model_dump(),
        #             gallery=tables.GalleryPublic.model_validate(gallery),
        #             parents=[tables.GalleryPublic.model_validate(
        #                 parent) for parent in await gallery.get_parents(session)],
        #             children=[tables.GalleryPublic.model_validate(
        #                 child) for child in gallery.children]
        #         )


class PagesAdminRouter(_Base):
    _ADMIN = True

    def _set_routes(self):
        pass
