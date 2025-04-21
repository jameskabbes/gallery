from fastapi import Depends, Request, Response, Form, status
from pydantic import BaseModel
from typing import Annotated, cast


from . import base
from .. import types
from ..auth import utils as auth_utils, exceptions as auth_exceptions
from ..models.tables import user as user_model_module, user_access_token as user_access_token_model_module
from ..models.tables.bases import auth_credential
from ..config import settings


class PostTokenResponse(BaseModel):
    access_token: types.JwtEncodedStr
    token_type: str


class PostLoginWithPasswordResponse(auth_utils.GetUserSessionInfoNestedReturn):
    pass


class PostLoginWithMagicLinkRequest(BaseModel):
    token: types.JwtEncodedStr


class PostLoginWithMagicLinkResponse(auth_utils.GetUserSessionInfoNestedReturn):
    pass


class PostLoginWithOTPEmailRequest(BaseModel):
    code: types.OTP.code
    email: types.User.email


class PostLoginWithGoogleRequest(BaseModel):
    access_token: str


class PostLoginWithGoogleResponse(auth_utils.GetUserSessionInfoNestedReturn):
    pass


class PostLoginWithOTPPhoneNumberRequest(BaseModel):
    code: types.OTP.code
    phone_number: types.User.phone_number


class PostSignUpRequest(BaseModel):
    token: str


class PostSignUpResponse(auth_utils.GetUserSessionInfoNestedReturn):
    pass


class PostRequestSignUpEmailRequest(BaseModel):
    email: types.User.email


class PostRequestSignUpSMSRequest(BaseModel):
    phone_number: types.User.phone_number


class PostRequestMagicLinkEmailRequest(BaseModel):
    email: types.User.email


class PostRequestMagicLinkSMSRequest(BaseModel):
    phone_number: types.User.phone_number


class PostRequestOTPEmailRequest(BaseModel):
    email: types.User.email


class PostRequestOTPSMSRequest(BaseModel):
    phone_number: types.User.phone_number


class AuthRouter(base.Router):
    _PREFIX = '/auth'
    _TAGS = ['Auth']

    def _set_routes(self):

        @self.router.get('/')
        async def get_auth_root(authorization: Annotated[auth_utils.GetAuthReturn, Depends(auth_utils.make_get_auth_dependency(c=self.client, raise_exceptions=False))]) -> auth_utils.GetUserSessionInfoNestedReturn:
            return auth_utils.get_user_session_info(authorization)

        @self.router.post('/token/')
        async def post_token(
            user: Annotated[user_model_module.User, Depends(auth_utils.make_authenticate_user_with_username_and_password_dependency(c=self.client))],
            response: Response,
            stay_signed_in: bool = Form(
                self.client.auth['stay_signed_in_default'])
        ) -> PostTokenResponse:
            async with self.client.AsyncSession() as session:

                user_access_token = await user_access_token_model_module.UserAccessToken.create({
                    'authorized_user_id': user.id,
                    'c': self.client,
                    'create_model': user_access_token_model_module.UserAccessTokenAdminCreate(
                        user_id=user.id,
                        expiry=auth_credential.lifespan_to_expiry(self.client.auth[
                            'credential_lifespans']['access_token']),
                    ),
                    'session': session
                })

                encoded_jwt = self.client.jwt_encode(
                    cast(dict, user_access_token.to_payload()))

                auth_utils.set_access_token_cookie(response, encoded_jwt, None if not stay_signed_in else auth_credential.lifespan_to_expiry(
                    self.client.auth['credential_lifespans']['access_token']))
                return PostTokenResponse(access_token=encoded_jwt, token_type='bearer')

        @self.router.post('/login/password/', responses={status.HTTP_401_UNAUTHORIZED: {'description': 'Could not validate credentials', 'model': auth_utils.DetailOnlyResponse}})
        async def post_login_password(
            user: Annotated[user_model_module.User, Depends(auth_utils.make_authenticate_user_with_username_and_password_dependency(c=self.client))],
            response: Response,
            request: Request,
            stay_signed_in: bool = Form(
                self.client.auth['stay_signed_in_default'])
        ) -> PostLoginWithPasswordResponse:

            async with self.client.AsyncSession() as session:

                tokken_lifespan = self.client.auth['credential_lifespans']['access_token']

                user_access_token = await user_access_token_model_module.UserAccessToken.create({
                    'authorized_user_id': user.id,
                    'c': self.client,
                    'create_model': user_access_token_model_module.UserAccessTokenAdminCreate(
                        user_id=user.id,
                        expiry=auth_credential.lifespan_to_expiry(self.client.auth[
                            'credential_lifespans']['access_token']),
                    ),
                    'session': session
                })

                encoded_jwt = self.client.jwt_encode(
                    cast(dict, user_access_token.to_payload()))

                auth_utils.set_access_token_cookie(response, encoded_jwt, None if not stay_signed_in else auth_credential.lifespan_to_expiry(
                    self.client.auth['credential_lifespans']['access_token']))

                return PostLoginWithPasswordResponse(
                    auth=auth_utils.GetUserSessionInfoReturn(
                        user=user_model_module.UserPrivate.model_validate(
                            user),
                        scope_ids=set(
                            settings.USER_ROLE_ID_SCOPE_IDS[user.user_role_id]),
                        access_token=user_access_token_model_module.UserAccessTokenPublic.model_validate(
                            user_access_token),
                    ))

        # @self.router.post('/login/magic-link/', responses={status.HTTP_401_UNAUTHORIZED: {'description': 'Invalid token', 'model': DetailOnlyResponse}})
        # async def post_login_magic_link(
        #         response: Response,
        #         model: PostLoginWithMagicLinkRequest
        # ) -> PostLoginWithMagicLinkResponse:

        #     authorization = await get_auth_from_token(token=model.token, permitted_auth_credential_types={
        #     ccess_token'}, override_lifetime=self.client.auth['credential_lifespans']['magic_link'])

        #     if authorization.exception:
        #         raise authorization.exception()

        #     async with self.client.AsyncSession() as session:

        #     ken_lifespan = self.client.auth['credential_lifespans']['access_token']
        #         user_access_token = await models.UserAccessToken.api_post(models.UserAccessToken.PostParams.model_construct(
        #             session=session, c=c,  authorized_user_id=authorization._user_id, create_model=models.UserAccessTokenAdminCreate(
        #                 user_id=authorization._user_id, lifespan=token_lifespan
        #             )))

        #         auth.set_access_token_cookie(response, c.jwt_encode(
        #             user_access_token.to_payload()), token_lifespan)

        #         # one time link, delete the auth_credential
        #         session.delete(authorization.auth_credential)
        #         session.commit()

        #         return PostLoginWithMagicLinkResponse(
        #             auth=GetAuthBaseReturn(
        #                 user=models.UserPrivate.model_validate(
        #                     authorization.user),
        #                 scope_ids=set(
        #                     settings.USER_ROLE_ID_SCOPE_IDS[authorization.user.user_role_id]),
        #                 auth_credential=AuthCredentialIdTypeAndExpiry(
        #                     id=user_access_token.id, type='access_token', expiry=user_access_token.expiry)
        #             )
        #         )

        # @self.router.post('/login/otp/email/')
        # async def post_login_otp_email(
        #         model: PostLoginWithOTPEmailRequest,
        #         response: Response) -> PostLoginWithOTPResponse:

        #     async with self.client.AsyncSession() as session:
        #         user = session.exec(select(models.User).where(
        #             models.User.email == model.email)).one_or_none()
        #         return await post_login_otp(session, user, response, model.code)

        # @self.router.post('/login/otp/phone_number/')
        # async def post_login_otp_phone_number(
        #     model: PostLoginWithOTPPhoneNumberRequest,
        #     response: Response
        # ) -> PostLoginWithOTPResponse:

        #     async with self.client.AsyncSession() as session:
        #         user = session.exec(select(models.User).where(
        #             models.User.phone_number == model.phone_number)).one_or_none()
        #         return await post_login_otp(session, user, response, model.code)

        # @self.router.post("/login/google/", responses={status.HTTP_400_BAD_REQUEST: {'description': 'Invalid token', 'model': DetailOnlyResponse}})
        # async def post_login_google(request_token: PostLoginWithGoogleRequest, response: Response) -> PostLoginWithGoogleResponse:

        #     async with httpx.AsyncClient() as client:
        #         res = await client.get('https://www.googleapis.com/oauth2/v3/userinfo?access_token={}'.format(request_token.access_token))
        #         res.raise_for_status()
        #         user_info = res.json()

        #     # fields: sub, name, given_name, family_name, picture, email, email_verified
        #     email = user_info.get('email')
        #     if not email:
        #         raise HTTPException(status.HTTP_400_BAD_REQUEST,
        #                             detail='Invalid token')
        #     async with self.client.AsyncSession() as session:

        #         user = session.exec(select(models.User).where(
        #             models.User.email == email)).one_or_none()
        #         if not user:
        #             user = await models.User.api_post(models.User.PostParams.model_construct(
        #                 session=session, c=c, authorized_user_id=None, admin=True, create_model=models.UserAdminCreate(email=email, user_role_id=settings.USER_ROLE_NAME_MAPPING['user'])
        #             ))

        #     ken_lifespan = self.client.auth['credential_lifespans']['access_token']

        #         user_access_token = await models.UserAccessToken.api_post(models.UserAccessToken.PostParams.model_construct(session=session, c=c,  authorized_user_id=user._id, create_model=models.UserAccessTokenAdminCreate(
        #             user_id=user.id, lifespan=token_lifespan
        #         )))

        #         auth.set_access_token_cookie(response, c.jwt_encode(
        #             user_access_token.to_payload()), token_lifespan)

        #         return PostLoginWithGoogleResponse(
        #             auth=GetAuthBaseReturn(
        #                 user=models.UserPrivate.model_validate(user),
        #                 scope_ids=set(
        #                     settings.USER_ROLE_ID_SCOPE_IDS[user.user_role_id]),
        #                 auth_credential=AuthCredentialIdTypeAndExpiry(
        #                     id=user_access_token.id, type='access_token', expiry=user_access_token.expiry)
        #             )
        #         )

        # @self.router.post('/signup/')
        # async def post_signup(response: Response, model: PostSignUpRequest) -> PostSignUpResponse:

        #     authorization = await get_auth_from_token(
        #         token=model.token,
        #         permitted_auth_credential_types={'sign_up'},
        #     erride_lifetime=self.client.auth['credential_lifespans']['request_sign_up'])

        #     async with self.client.AsyncSession() as session:
        #         sign_up: models.SignUp = authorization.auth_credential

        #         user_create_admin = models.UserAdminCreate(
        #             email=sign_up.email, user_role_id=settings.USER_ROLE_NAME_MAPPING['user'])

        #         user = await models.User.api_post(models.User.PostParams.model_construct(
        #             session=session, c=c, authorized_user_id=None, create_model=user_create_admin
        #         ))

        #     ken_lifespan = self.client.auth['credential_lifespans']['access_token']
        #         user_access_token = await models.UserAccessToken.api_post(models.UserAccessToken.PostParams.model_construct(
        #             session=session, c=c,  authorized_user_id=user._id, create_model=models.UserAccessTokenAdminCreate(
        #                 user_id=user._id, type='access_token', lifespan=token_lifespan
        #             )))

        #         auth.set_access_token_cookie(response, c.jwt_encode(
        #             user_access_token.to_payload()), token_lifespan)

        #         return PostSignUpResponse(
        #             auth=GetAuthBaseReturn(
        #                 user=models.UserPrivate.model_validate(user),
        #                 scope_ids=set(
        #                     settings.USER_ROLE_ID_SCOPE_IDS[user.user_role_id]),
        #                 auth_credential=AuthCredentialIdTypeAndExpiry(
        #                     id=user_access_token.id, type='access_token', expiry=user_access_token.expiry)
        #             )
        #         )

        # @self.router.post('/request/signup/email/')
        # async def post_request_sign_up_email(
        #     model: PostRequestSignUpEmailRequest,
        #     background_tasks: BackgroundTasks
        # ):

        #     async with self.client.AsyncSession() as session:
        #         user = session.exec(select(models.User).where(
        #             models.User.email == model.email)).one_or_none()
        #         background_tasks.add_task(
        #             send_signup_link, session, user, email=model.email)
        #         return Response()

        # @self.router.post('/request/signup/sms/')
        # async def post_request_sign_up_sms(
        #     model: PostRequestSignUpSMSRequest,
        #     background_tasks: BackgroundTasks
        # ):
        #     async with self.client.AsyncSession() as session:
        #         user = session.exec(select(models.User).where(
        #             models.User.phone_number == model.phone_number)).one_or_none()
        #         background_tasks.add_task(
        #             send_signup_link, session, user, phone_number=model.phone_number)
        #         return Response()

        # @self.router.post('/request/magic-link/email/')
        # async def post_request_magic_link_email(model: PostRequestMagicLinkEmailRequest, background_tasks: BackgroundTasks):

        #     async with self.client.AsyncSession() as session:
        #         user = session.exec(select(models.User).where(
        #             models.User.email == model.email)).one_or_none()
        #         if user:
        #             background_tasks.add_task(
        #                 send_magic_link, session, user, email=model.email)
        #     return Response()

        # @self.router.post('/request/magic-link/sms/')
        # async def post_request_magic_link_sms(model: PostRequestMagicLinkSMSRequest, background_tasks: BackgroundTasks):
        #     async with self.client.AsyncSession() as session:
        #         user = session.exec(select(models.User).where(
        #             models.User.email == model.phone_number)).one_or_none()
        #         if user:
        #             background_tasks.add_task(
        #                 send_magic_link, session, user, phone_number=model.phone_number)
        #     return Response()

        # @self.router.post('/request/otp/email/')
        # async def post_request_otp_email(model: PostRequestOTPEmailRequest, background_tasks: BackgroundTasks):

        #     async with self.client.AsyncSession() as session:
        #         user = session.exec(select(models.User).where(
        #             models.User.email == model.email)).one_or_none()

        #         if user:
        #             background_tasks.add_task(
        #                 send_otp, session, user, email=model.email)
        #     return Response()

        # @self.router.post('/request/otp/sms/')
        # async def post_request_otp_email(model: PostRequestOTPSMSRequest, background_tasks: BackgroundTasks):

        #     async with self.client.AsyncSession() as session:
        #         user = session.exec(select(models.User).where(
        #             models.User.phone_number == model.phone_number)).one_or_none()
        #         if user:
        #             background_tasks.add_task(
        #                 send_otp, session, user, phone_number=model.phone_number)
        #     return Response()

        # @self.router.post('/logout/')
        # async def logout(response: Response, authorization: Annotated[GetAuthorizationReturn, Depends(
        #         auth_utils.make_get_auth_dependency(c=self.client, raise_exceptions=False, permitted_auth_credential_types={'access_token'}))]) -> DetailOnlyResponse:

        #     if authorization.auth_credential:
        #         if authorization.auth_credential.auth_type == 'access_token':
        #             async with self.client.AsyncSession() as session:
        #                 await models.UserAccessToken.api_delete(models.UserAccessToken.DeleteParams.model_construct(
        #                     session=session, c=c, authorized_user_id=authorization._user_id, id=authorization.auth_credential.id
        #                 ))

        #     auth.delete_access_token_cookie(response)
        #     return DetailOnlyResponse(detail='Logged out')
