from fastapi import Depends, status
from sqlmodel import select, func
from pydantic import BaseModel
from ..models.tables import ApiKey as ApiKeyTable
from ..services.api_key import ApiKey as ApiKeyService
from ..schemas import api_key as api_key_schema, pagination as pagination_schema, api as api_schema, order_by as order_by_schema
from . import base
from .. import types
from typing import Annotated, cast
from ..auth import utils as auth_utils

from collections.abc import Sequence


class _Base(base.Router):
    _PREFIX = '/pages'
    _TAGS = ['Page']


class PagesRouter(_Base):
    _ADMIN = False

    def _set_routes(self):
        @self.router.get('/profile/', tags=[tables.User._ROUTER_TAG])
        async def get_pages_profile(authorization: typing.Annotated[GetAuthorizationReturn, Depends(
                make_get_auth_dependency())]) -> GetProfilePageResponse:

            return GetProfilePageResponse(
                **get_auth(authorization).model_dump(),
                user=tables.UserPrivate.model_validate(authorization.user)
            )


class PagesAdminRouter(_Base):
    _ADMIN = True

    def _set_routes(self):
        pass


class GetProfilePageResponse(GetAuthReturn):
    user: tables.UserPrivate | None = None


class GetHomePageResponse(GetAuthReturn):
    pass


@self.router.get('/home/')
async def get_home_page(authorization: typing.Annotated[GetAuthorizationReturn, Depends(make_get_auth_dependency(raise_exceptions=False))]) -> GetHomePageResponse:
    return GetHomePageResponse(
        **get_auth(authorization).model_dump()
    )


class GetSettingsPageResponse(GetAuthReturn):
    pass


@self.router.get('/settings/')
async def get_settings_page(
        authorization: typing.Annotated[GetAuthorizationReturn, Depends(
            make_get_auth_dependency(raise_exceptions=False))]
) -> GetSettingsPageResponse:
    return GetSettingsPageResponse(
        **get_auth(authorization).model_dump()
    )


class GetSettingsApiKeysPageResponse(GetAuthReturn):
    api_key_count: int
    api_keys: list[tables.ApiKeyPrivate]


@self.router.get('/settings/api-keys/', tags=[tables.ApiKey._ROUTER_TAG])
async def get_settings_api_keys_page(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(make_get_auth_dependency())],
    get_api_keys_query_params: GetApiKeysQueryParamsReturn = Depends(
        get_api_keys_query_params)
) -> GetSettingsApiKeysPageResponse:
    return GetSettingsApiKeysPageResponse(
        **get_auth(authorization).model_dump(),
        api_key_count=await get_user_api_keys_count(authorization),
        api_keys=await get_user_api_keys(authorization, get_api_keys_query_params)
    )


class GetSettingsUserAccessTokensPageResponse(GetAuthReturn):
    user_access_token_count: int
    user_access_tokens: list[tables.UserAccessToken]


@self.router.get('/settings/user-access-tokens/', tags=[tables.UserAccessToken._ROUTER_TAG])
async def get_settings_user_access_tokens_page(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(make_get_auth_dependency())],
    pagination: tables.Pagination = Depends(user_access_token_pagination)
) -> GetSettingsUserAccessTokensPageResponse:
    return GetSettingsUserAccessTokensPageResponse(
        **get_auth(authorization).model_dump(),
        user_access_token_count=await get_user_access_tokens_count(authorization),
        user_access_tokens=await get_user_access_tokens(authorization, pagination)
    )


class GetStylesPageResponse(GetAuthReturn):
    pass


@self.router.get('/styles/')
async def get_styles_page(authorization: typing.Annotated[GetAuthorizationReturn, Depends(make_get_auth_dependency(raise_exceptions=False))]) -> GetStylesPageResponse:
    return GetStylesPageResponse(
        **get_auth(authorization).model_dump()
    )


class GetGalleryPageResponse(GetAuthReturn):
    gallery: tables.GalleryPublic
    parents: list[tables.GalleryPublic]
    children: list[tables.GalleryPublic]


@self.router.get('/galleries/{gallery_id}/', responses={status.HTTP_404_NOT_FOUND: {"description": tables.Gallery.not_found_message(), 'model': NotFoundResponse}}, tags=[tables.Gallery._ROUTER_TAG])
async def get_gallery_page(
    gallery_id: tables.GalleryTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(raise_exceptions=False))],
    root: bool = Query(False),
) -> GetGalleryPageResponse:

    async with c.AsyncSession() as session:
        if root:
            if not authorization.isAuthorized:
                raise tables.Gallery.not_found_exception()

            gallery = await tables.Gallery.get_root_gallery(session, authorization._user_id)
            gallery_id = gallery._id

        else:
            gallery = await tables.Gallery.api_get(tables.Gallery.GetParams.model_construct(
                session=session, c=c,  authorized_user_id=authorization._user_id, id=gallery_id
            ))

        return GetGalleryPageResponse(
            **get_auth(authorization).model_dump(),
            gallery=tables.GalleryPublic.model_validate(gallery),
            parents=[tables.GalleryPublic.model_validate(
                parent) for parent in await gallery.get_parents(session)],
            children=[tables.GalleryPublic.model_validate(
                child) for child in gallery.children]
        )
