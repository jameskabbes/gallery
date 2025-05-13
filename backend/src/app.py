from fastapi import FastAPI
from contextlib import asynccontextmanager
# from fastapi import FastAPI, HTTPException, Request
# from fastapi.responses import JSONResponse

# from gallery import client
# from gallery.routers import user, auth, user_access_token, api_key_scope, gallery, api_key, pages
# from backend.src.config import settings
# from gallery.auth import utils as auth_utils


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('startingup')
    yield
    print('closingdown')

app = FastAPI(lifespan=lifespan)


# @app.exception_handler(HTTPException)
# async def custom_http_exception_handler(request: Request, exc: HTTPException):

#     response = JSONResponse(status_code=exc.status_code,
#                             content={"detail": exc.detail}, headers=exc.headers)

#     # in get_auhorization, a special header 'X-Auth-Logout' is set, signaling the user should be logged out
#     if exc.headers and exc.headers.get(settings.HEADER_KEYS['auth_logout']) is not None:
#         auth_utils.delete_access_token_cookie(response)
#     return response


# app.include_router(auth.AuthRouter(c).router)
# app.include_router(user.UserRouter(c).router)
# app.include_router(gallery.GalleryRouter(c).router)
# app.include_router(user_access_token.UserAccessTokenRouter(c).router)
# app.include_router(api_key.ApiKeyRouter(c).router)
# app.include_router(api_key_scope.ApiKeyScopeRouter(c).router)
# app.include_router(pages.PagesRouter(c).router)

# app.include_router(user.UserAdminRouter(c).router)
# app.include_router(gallery.GalleryAdminRouter(c).router)
# app.include_router(user_access_token.UserAccessTokenAdminRouter(c).router)
# app.include_router(api_key.ApiKeyAdminRouter(c).router)
# app.include_router(api_key_scope.ApiKeyScopeAdminRouter(c).router)
