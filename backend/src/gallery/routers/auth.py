from fastapi import Depends, Request, Response, Form, status, BackgroundTasks
from sqlmodel import select
from pydantic import BaseModel
from typing import Annotated, cast


from . import base
from .. import types
from ..auth import utils as auth_utils, exceptions as auth_exceptions
from ..config import settings

from ..schemas import user_access_token as user_access_token_schema, user as user_schema, api as api_schema, sign_up as sign_up_schema
from ..models.tables import User, UserAccessToken
from ..models.models import SignUp
from ..services.user import User as UserService
from ..services.user_access_token import UserAccessToken as UserAccessTokenService
from ..services import auth_credential as auth_credential_service


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

    _ADMIN = False
    _PREFIX = '/auth'
    _TAGS = ['Auth']

    def _set_routes(self):

        @self.router.get('/')
        async def get_auth_root(authorization: Annotated[auth_utils.GetAuthReturn, Depends(auth_utils.make_get_auth_dependency(c=self.client, raise_exceptions=False))]) -> auth_utils.GetUserSessionInfoNestedReturn:
            return auth_utils.get_user_session_info(authorization)

        @self.router.post('/token/')
        async def post_token(
            user: Annotated[User, Depends(auth_utils.make_authenticate_user_with_username_and_password_dependency(c=self.client))],
            response: Response,
            stay_signed_in: bool = Form(
                self.client.auth['stay_signed_in_default'])
        ) -> PostTokenResponse:
            async with self.client.AsyncSession() as session:

                user_access_token = await UserAccessTokenService.create({
                    'authorized_user_id': user.id,
                    'c': self.client,
                    'create_model': user_access_token_schema.UserAccessTokenAdminCreate(
                        user_id=user.id,
                        expiry=auth_credential_service.lifespan_to_expiry(self.client.auth[
                            'credential_lifespans']['access_token']),
                    ),
                    'session': session
                })

                encoded_jwt = self.client.jwt_encode(
                    cast(dict, UserAccessTokenService.to_jwt_payload(user_access_token)))

                auth_utils.set_access_token_cookie(response, encoded_jwt, None if not stay_signed_in else auth_credential_service.lifespan_to_expiry(
                    self.client.auth['credential_lifespans']['access_token']))
                return PostTokenResponse(access_token=encoded_jwt, token_type='bearer')

        @self.router.post('/login/password/', responses={status.HTTP_401_UNAUTHORIZED: {'description': 'Could not validate credentials', 'model': api_schema.DetailOnlyResponse}})
        async def post_login_password(
            user: Annotated[User, Depends(auth_utils.make_authenticate_user_with_username_and_password_dependency(c=self.client))],
            response: Response,
            request: Request,
            stay_signed_in: bool = Form(
                self.client.auth['stay_signed_in_default'])
        ) -> PostLoginWithPasswordResponse:

            async with self.client.AsyncSession() as session:

                tokken_lifespan = self.client.auth['credential_lifespans']['access_token']

                user_access_token = await UserAccessTokenService.create({
                    'authorized_user_id': user.id,
                    'c': self.client,
                    'create_model': user_access_token_schema.UserAccessTokenAdminCreate(
                        user_id=user.id,
                        expiry=auth_credential_service.lifespan_to_expiry(self.client.auth[
                            'credential_lifespans']['access_token']),
                    ),
                    'session': session
                })

                encoded_jwt = self.client.jwt_encode(
                    cast(dict, UserAccessTokenService.to_jwt_payload(user_access_token)))

                auth_utils.set_access_token_cookie(response, encoded_jwt, None if not stay_signed_in else auth_credential_service.lifespan_to_expiry(
                    self.client.auth['credential_lifespans']['access_token']))

                user_private = user_schema.UserPrivate.model_validate(user)

                return PostLoginWithPasswordResponse(
                    auth=auth_utils.GetUserSessionInfoReturn(
                        user=user_schema.UserPrivate.model_validate(
                            user),
                        scope_ids=set(
                            settings.USER_ROLE_ID_SCOPE_IDS[user.user_role_id]),
                        access_token=user_access_token_schema.UserAccessTokenPublic.model_validate(
                            user_access_token),
                    ))

        @self.router.post('/login/magic-link/', responses={status.HTTP_401_UNAUTHORIZED: {'description': 'Invalid token', 'model': api_schema.DetailOnlyResponse}})
        async def post_login_magic_link(
                response: Response,
                model: PostLoginWithMagicLinkRequest
        ) -> PostLoginWithMagicLinkResponse:

            authorization = await auth_utils.get_auth_from_auth_credential_jwt(
                c=self.client,
                token=model.token,
                permitted_types={'access_token'},
                override_lifetime=self.client.auth['credential_lifespans']['magic_link']
            )

            if authorization.exception:
                raise auth_exceptions.Base(authorization.exception)

            auth_credential = cast(
                UserAccessToken, authorization.auth_credential)

            async with self.client.AsyncSession() as session:
                token_lifespan = self.client.auth['credential_lifespans']['access_token']
                user_access_token = await UserAccessTokenService.create(
                    {
                        'session': session,
                        'c': self.client,
                        'create_model': user_access_token_schema.UserAccessTokenAdminCreate(
                            user_id=auth_credential.user_id,
                            expiry=auth_credential_service.lifespan_to_expiry(
                                token_lifespan),
                        )

                    }
                )

                auth_utils.set_access_token_cookie(response, self.client.jwt_encode(
                    dict(UserAccessTokenService.to_jwt_payload(user_access_token))), expiry=auth_credential_service.lifespan_to_expiry(token_lifespan))

                # one time link, delete the auth_credential
                await session.delete(auth_credential)
                await session.commit()

            return PostLoginWithMagicLinkResponse(
                auth=auth_utils.GetUserSessionInfoReturn(
                    user=user_schema.UserPrivate.model_validate(
                        authorization.user),
                    scope_ids=set(
                        settings.USER_ROLE_ID_SCOPE_IDS[cast(user_schema.UserPrivate, authorization.user).user_role_id]),
                    access_token=user_access_token_schema.UserAccessTokenPublic.model_validate(
                        user_access_token
                    )
                )
            )

        @self.router.post('/login/otp/email/')
        async def post_login_otp_email(
                model: PostLoginWithOTPEmailRequest,
                response: Response) -> auth_utils.PostLoginWithOTPResponse:

            async with self.client.AsyncSession() as session:
                user = (await session.exec(select(User).where(
                    User.email == model.email))).one_or_none()
                return await auth_utils.post_login_otp(session, self.client, user, response, model.code)

        @self.router.post('/login/otp/phone_number/')
        async def post_login_otp_phone_number(
            model: PostLoginWithOTPPhoneNumberRequest,
            response: Response
        ) -> auth_utils.PostLoginWithOTPResponse:

            async with self.client.AsyncSession() as session:
                user = (await session.exec(select(User).where(
                    User.phone_number == model.phone_number))).one_or_none()
                return await auth_utils.post_login_otp(session, self.client, user, response, model.code)

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

        #         user_access_token = await UserAccessTokenService.create({
        #
        #
        # models.UserAccessToken.PostParams.model_construct(session=session, c=c,  authorized_user_id=user._id, create_model=models.UserAccessTokenAdminCreate(
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

        @self.router.post('/signup/')
        async def post_signup(response: Response, model: PostSignUpRequest) -> PostSignUpResponse:

            authorization = await auth_utils.get_auth_from_auth_credential_jwt(
                c=self.client,
                token=model.token,
                permitted_types={'sign_up'},
                override_lifetime=self.client.auth['credential_lifespans']['request_sign_up'])

            # double check the user doesn't already exist
            async with self.client.AsyncSession() as session:

                if (await session.exec(select(User).where(
                        User.email == cast(SignUp, authorization.auth_credential).email))).one_or_none() is not None:
                    raise auth_exceptions.Base({
                        'status_code': status.HTTP_409_CONFLICT,
                        'detail': 'User already exists'
                    })

            async with self.client.AsyncSession() as session:
                sign_up = cast(SignUp,
                               authorization.auth_credential)

                user = await UserService.create({
                    'admin': True,
                    'c': self.client,
                    'session': session,
                    'create_model': user_schema.UserAdminCreate(
                        email=sign_up.email, user_role_id=settings.USER_ROLE_NAME_MAPPING['user'])
                })

            token_expiry = auth_credential_service.lifespan_to_expiry(
                self.client.auth['credential_lifespans']['access_token'])

            user_access_token = await UserAccessTokenService.create({
                'session': session,
                'c': self.client,
                'authorized_user_id': user.id,
                'create_model': user_access_token_schema.UserAccessTokenAdminCreate(
                    user_id=user.id,
                    expiry=token_expiry
                )
            })

            auth_utils.set_access_token_cookie(
                response,
                self.client.jwt_encode(
                    cast(dict, UserAccessTokenService.to_jwt_payload(user_access_token))),
                expiry=token_expiry)

            return PostSignUpResponse(
                auth=auth_utils.GetUserSessionInfoReturn(
                    user=user_schema.UserPrivate.model_validate(user),
                    scope_ids=set(
                        settings.USER_ROLE_ID_SCOPE_IDS[user.user_role_id]),
                    access_token=user_access_token_schema.UserAccessTokenPublic.model_validate(
                        user_access_token),
                )
            )

        @self.router.post('/request/signup/')
        async def post_request_sign_up_email(
            model: PostRequestSignUpEmailRequest,
            background_tasks: BackgroundTasks
        ):

            async with self.client.AsyncSession() as session:
                user = (await session.exec(select(User).where(
                    User.email == model.email))).one_or_none()
                background_tasks.add_task(
                    auth_utils.send_signup_link, session, self.client, user, email=model.email)
                return Response()

        @self.router.post('/request/magic-link/email/')
        async def post_request_magic_link_email(model: PostRequestMagicLinkEmailRequest, background_tasks: BackgroundTasks):

            async with self.client.AsyncSession() as session:
                user = (await session.exec(select(User).where(
                    User.email == model.email))).one_or_none()
                if user:
                    background_tasks.add_task(
                        auth_utils.send_magic_link, session, self.client, user, email=model.email)
            return Response()

        @self.router.post('/request/magic-link/sms/')
        async def post_request_magic_link_sms(model: PostRequestMagicLinkSMSRequest, background_tasks: BackgroundTasks):
            async with self.client.AsyncSession() as session:
                user = (await session.exec(select(User).where(
                    User.phone_number == model.phone_number))).one_or_none()
                if user:
                    background_tasks.add_task(
                        auth_utils.send_magic_link, session, self.client, user, phone_number=model.phone_number)
            return Response()

        @self.router.post('/request/otp/email/')
        async def post_request_otp_email(model: PostRequestOTPEmailRequest, background_tasks: BackgroundTasks):

            async with self.client.AsyncSession() as session:
                user = (await session.exec(select(User).where(
                    User.email == model.email))).one_or_none()

                if user:
                    background_tasks.add_task(
                        auth_utils.send_otp, session, self.client, user, email=model.email)
            return Response()

        @self.router.post('/request/otp/sms/')
        async def post_request_otp_sms(model: PostRequestOTPSMSRequest, background_tasks: BackgroundTasks):

            async with self.client.AsyncSession() as session:
                user = (await session.exec(select(User).where(
                    User.phone_number == model.phone_number))).one_or_none()
                if user:
                    background_tasks.add_task(
                        auth_utils.send_otp, session, self.client, user, phone_number=model.phone_number)
            return Response()

        @self.router.post('/logout/')
        async def logout(response: Response, authorization: Annotated[auth_utils.GetAuthReturn[UserAccessToken], Depends(
                auth_utils.make_get_auth_dependency(c=self.client, raise_exceptions=False, permitted_types={'access_token'}))]) -> api_schema.DetailOnlyResponse:

            if authorization.isAuthorized:
                async with self.client.AsyncSession() as session:
                    await UserAccessTokenService.delete({
                        'authorized_user_id': cast(types.User.id, authorization._user_id),
                        'c': self.client,
                        'session': session,
                        'id': UserAccessTokenService.model_id(cast(UserAccessToken, authorization.auth_credential))
                    })

            auth_utils.delete_access_token_cookie(response)
            return api_schema.DetailOnlyResponse(detail='Logged out')
