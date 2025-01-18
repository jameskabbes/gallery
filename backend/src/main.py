import uvicorn
from fastapi import FastAPI, HTTPException, Query, status, Response, Depends, Request, BackgroundTasks, Form, File, UploadFile, APIRouter, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2, OAuth2PasswordRequestForm, OAuth2PasswordBearer, APIKeyHeader
from fastapi.security.utils import get_authorization_scheme_param
from contextlib import asynccontextmanager
from sqlalchemy import and_
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import func
from gallery import get_client, models, utils, auth, client, types, config
import datetime
from sqlmodel import Session, SQLModel, select
import typing
import httpx
import jwt
from jwt.exceptions import InvalidTokenError, MissingRequiredClaimError, DecodeError
from pydantic import BaseModel, model_validator
import datetime
from functools import wraps
from urllib.parse import urlencode
import pathlib
import shutil
from google.oauth2 import id_token
from google.auth.transport import requests


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('startingup')
    yield
    print('closingdown')

app = FastAPI(lifespan=lifespan)
c = get_client()


class OAuth2PasswordBearerMultiSource(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: typing.Optional[str] = None,
        scopes: typing.Optional[dict[str, str]] = None,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(
            password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=False)

    async def __call__(self, request: Request) -> types.JwtEncodedStr:
        # change to accept access token from Authorization header

        token: types.JwtEncodedStr | None = None

        # Authorization: bearer <token>
        authorization = request.headers.get("Authorization")
        if authorization:
            scheme, param = get_authorization_scheme_param(authorization)
            if scheme.lower() == "bearer":
                token = param

        # HTTP-only Cookie
        cookie_access_token = request.cookies.get(auth.ACCESS_TOKEN_COOKIE_KEY)
        if cookie_access_token:
            if token != None:
                raise auth.both_authorization_header_and_cookie_exception()
            token = cookie_access_token

        return token


oauth2_scheme = OAuth2PasswordBearerMultiSource(
    tokenUrl="auth/token/")


class DetailOnlyResponse(BaseModel):
    detail: str


class NotFoundResponse(DetailOnlyResponse):
    pass


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):

    response = JSONResponse(status_code=exc.status_code,
                            content={"detail": exc.detail}, headers=exc.headers)

    # in get_auhorization, a special header 'X-Auth-Logout' is set, signaling the user should be logged out
    if exc.headers and exc.headers.get(config.HEADER_KEYS['auth_logout']) != None:
        auth.delete_access_token_cookie(response)
    return response


class MakeGetAuthorizationDependencyKwargs(typing.TypedDict, total=False):
    required_scopes: typing.Optional[set[types.ScopeTypes.name]]
    permitted_auth_credential_types: typing.Optional[set[models.AuthCredentialTypes.type]]
    override_lifetime: typing.Optional[datetime.timedelta]


class GetAuthorizationReturn(BaseModel):
    isAuthorized: bool = False
    exception: typing.Optional[auth.AuthExceptionFunction] = None
    user: typing.Optional[models.UserPrivate] = None
    scope_ids: typing.Optional[set[types.ScopeTypes.id]] = None
    auth_credential: typing.Optional[models.AuthCredentialClass] = None

    @property
    def _user_id(self):
        if self.auth_credential:
            if self.auth_credential.user:
                return self.auth_credential.user._id
        else:
            return None


class GetAuthorizationFromTokenReturn(GetAuthorizationReturn):
    auth_credential: typing.Optional[models.AuthCredentialTokenClass] = None


async def get_auth_from_auth_credential_table_inst(
        session: Session,
        auth_credential_table_inst: models.AuthCredentialTableClass,
        required_scopes: set[types.ScopeTypes.name] = set(),
        override_lifetime: typing.Optional[datetime.timedelta] = None,
        dt_now=datetime.datetime.now(datetime.UTC),
) -> GetAuthorizationReturn:

    if not auth_credential_table_inst:
        return GetAuthorizationReturn(exception='authorization_expired')

    # if it expired, delete it
    if dt_now > auth_credential_table_inst.expiry:
        session.delete(auth_credential_table_inst)
        session.commit()
        return GetAuthorizationReturn(exception='authorization_expired')

    if override_lifetime != None:
        if dt_now > (auth_credential_table_inst.issued + override_lifetime):
            session.delete(auth_credential_table_inst)
            session.commit()
            return GetAuthorizationReturn(exception='authorization_expired')

    user = auth_credential_table_inst.user
    if user == None:
        return GetAuthorizationReturn(exception='user_not_found')

    scope_ids = await auth_credential_table_inst.get_scope_ids(session)

    required_scope_ids = set(
        [config.SCOPE_NAME_MAPPING[scope_name]
            for scope_name in required_scopes]
    )
    if not required_scope_ids.issubset(scope_ids):
        return GetAuthorizationReturn(exception='not_permitted')

    return GetAuthorizationReturn(
        isAuthorized=True,
        user=models.UserPrivate.model_validate(user),
        scope_ids=scope_ids,
        auth_credential=auth_credential_table_inst
    )


async def get_auth_from_token(
        token: typing.Optional[types.JwtEncodedStr] = None,
        required_scopes: set[types.ScopeTypes.name] = set(),
        permitted_auth_credential_types: set[models.AuthCredentialTokenType] = set(
            c.auth_type for c in models.AUTH_CREDENTIAL_TOKEN_CLASSES),
        override_lifetime: typing.Optional[datetime.timedelta] = None
) -> GetAuthorizationReturn:

    # make sure the token is a valid jwt
    try:
        payload: dict = c.jwt_decode(token)
    except:
        return GetAuthorizationReturn(exception=auth.improper_format_exception)

    # make sure "type" is in the jwt
    if models.AuthCredential.JwtIO._TYPE_CLAIM not in payload:
        return GetAuthorizationReturn(exception=auth.missing_required_claims_exception)

    # make sure the "type" is a permitted auth_credential type
    auth_type: models.AuthCredentialTypes.type = payload['type']
    if auth_type not in permitted_auth_credential_types:
        return GetAuthorizationReturn(exception=auth.authorization_type_not_permitted_exception)

    AuthCredentialClass = models.AUTH_CREDENTIAL_TYPE_TO_CLASS[auth_type]

    # validate the jwt claims
    if not AuthCredentialClass.validate_jwt_claims(payload):
        return GetAuthorizationReturn(exception=auth.missing_required_claims_exception)

    # decode the payload
    decoded_payload = AuthCredentialClass.decode(payload)
    decoded_payload['expiry'] = datetime.datetime.fromtimestamp(
        decoded_payload['expiry'], datetime.UTC)
    decoded_payload['issued'] = datetime.datetime.fromtimestamp(
        decoded_payload['issued'], datetime.UTC)

    auth_credential_from_jwt: models.AuthCredentialClass = AuthCredentialClass(
        **decoded_payload)

    dt_now = datetime.datetime.now(datetime.UTC)

    # check the dates from the jwt
    if dt_now > auth_credential_from_jwt.expiry:
        return GetAuthorizationReturn(exception=auth.authorization_expired_exception)
    if override_lifetime != None:
        if dt_now > auth_credential_from_jwt.issued + override_lifetime:
            return GetAuthorizationReturn(exception=auth.authorization_expired_exception)

    # if the auth_credentail is a table, it will need to be in the db
    # for example, SignUp is a JWT only credential, so it will not be in the db
    if issubclass(AuthCredentialClass, models.Table):
        with Session(c.db_engine) as session:
            auth_credential_from_db = await AuthCredentialClass.get_one_by_id(
                session, auth_credential_from_jwt._id)

            response = await get_auth_from_auth_credential_table_inst(
                session, auth_credential_from_db, required_scopes, override_lifetime, dt_now)
            return response
    else:
        # non-table auth_credentials have no scopes
        if required_scopes:
            return GetAuthorizationReturn(exception=auth.not_permitted_exception)

        return GetAuthorizationReturn(
            isAuthorized=True,
            user=None,
            scope_ids=set(),
            auth_credential=auth_credential_from_jwt
        )


def make_get_auth_dependency(raise_exceptions: bool = True, logout_on_exception: bool = True, **kwargs: typing.Unpack[MakeGetAuthorizationDependencyKwargs]):
    async def get_authorization_dependency(response: Response, auth_token: typing.Annotated[types.JwtEncodedStr | None, Depends(oauth2_scheme)]) -> GetAuthorizationReturn:
        get_authorization_return = await get_auth_from_token(token=auth_token, **kwargs)
        if get_authorization_return.exception:
            if raise_exceptions:

                exception_kwargs: auth.ExceptionKwargs = {
                    'logout_on_exception': logout_on_exception}

                raise get_authorization_return.exception(**exception_kwargs)
        return get_authorization_return
    return get_authorization_dependency


class AuthCredentialIdTypeAndExpiry(BaseModel):
    id: models.AuthCredentialId | None
    type: models.AuthCredentialTypes.type
    expiry: models.AuthCredentialTypes.expiry


class GetAuthBaseReturn(BaseModel):
    user: typing.Optional[models.UserPrivate]
    scope_ids: typing.Optional[set[types.ScopeTypes.id]]
    auth_credential: typing.Optional[AuthCredentialIdTypeAndExpiry]


assert config.SHARED_CONSTANTS['auth_key'] == 'auth'


class GetAuthReturn(BaseModel):
    auth: GetAuthBaseReturn


def get_auth(get_authorization_return: GetAuthorizationReturn) -> GetAuthReturn:

    return GetAuthReturn(auth=GetAuthBaseReturn(
        user=get_authorization_return.user,
        scope_ids=get_authorization_return.scope_ids,
        auth_credential=None if not get_authorization_return.auth_credential else
        AuthCredentialIdTypeAndExpiry(
            id=get_authorization_return.auth_credential._id,
            type=get_authorization_return.auth_credential.auth_type,
            expiry=get_authorization_return.auth_credential.expiry
        )
    ))


auth_router = APIRouter(prefix='/auth', tags=['Auth'])


@ auth_router.get('/')
async def get_auth_root(authorization: typing.Annotated[GetAuthorizationReturn, Depends(make_get_auth_dependency(raise_exceptions=False))]) -> GetAuthReturn:
    return get_auth(authorization)


async def authenticate_user_with_username_and_password(form_data: typing.Annotated[OAuth2PasswordRequestForm, Depends()]) -> models.User:

    with Session(c.db_engine) as session:
        user = await models.User.authenticate(
            session, form_data.username, form_data.password)
        if not user:
            raise auth.credentials_exception()
        return user


class PostTokenResponse(BaseModel):
    access_token: types.JwtEncodedStr
    token_type: str


@ auth_router.post('/token/')
async def post_token(
    user: typing.Annotated[models.User, Depends(authenticate_user_with_username_and_password)],
    response: Response,
    stay_signed_in: bool = Form(c.authentication['stay_signed_in_default'])
) -> PostTokenResponse:
    with Session(c.db_engine) as session:

        lifespan = None if not stay_signed_in else c.authentication[
            'expiry_timedeltas']['access_token']
        user_access_token = await models.UserAccessToken.api_post(
            session=session, c=c,  authorized_user_id=user._id, admin=False, create_model=models.UserAccessTokenAdminCreate(
                user_id=user._id, lifespan=lifespan
            ))

        encoded_jwt = c.jwt_encode(user_access_token.encode())
        auth.set_access_token_cookie(response, encoded_jwt, lifespan)
        return PostTokenResponse(access_token=encoded_jwt, token_type='bearer')


class PostLoginWithPasswordResponse(GetAuthReturn):
    pass


@ auth_router.post('/login/password/', responses={status.HTTP_401_UNAUTHORIZED: {'description': 'Could not validate credentials', 'model': DetailOnlyResponse}})
async def post_login_password(
    user: typing.Annotated[models.User, Depends(authenticate_user_with_username_and_password)],
    response: Response,
    request: Request,
    stay_signed_in: bool = Form(c.authentication['stay_signed_in_default'])
) -> PostLoginWithPasswordResponse:

    print(request.__dict__)

    with Session(c.db_engine) as session:

        token_lifespan = c.authentication['expiry_timedeltas']['access_token']
        user_access_token = await models.UserAccessToken.api_post(
            session=session, c=c,  authorized_user_id=user._id, admin=False, create_model=models.UserAccessTokenAdminCreate(
                user_id=user._id, lifespan=token_lifespan
            )
        )

        auth.set_access_token_cookie(response, c.jwt_encode(
            user_access_token.encode()), token_lifespan if stay_signed_in else None)

        return PostLoginWithPasswordResponse(
            auth=GetAuthBaseReturn(
                user=models.UserPrivate.model_validate(user),
                scope_ids=set(
                    config.USER_ROLE_ID_SCOPE_IDS[user.user_role_id]),
                auth_credential=AuthCredentialIdTypeAndExpiry(
                    id=user_access_token.id, type='access_token', expiry=user_access_token.expiry)
            )
        )


class PostLoginWithMagicLinkRequest(BaseModel):
    token: types.JwtEncodedStr


class PostLoginWithMagicLinkResponse(GetAuthReturn):
    pass


@ auth_router.post('/login/magic-link/', responses={status.HTTP_401_UNAUTHORIZED: {'description': 'Invalid token', 'model': DetailOnlyResponse}})
async def post_login_magic_link(
        response: Response,
        model: PostLoginWithMagicLinkRequest
) -> PostLoginWithMagicLinkResponse:

    authorization = await get_auth_from_token(token=model.token, permitted_auth_credential_types={
        'access_token'}, override_lifetime=c.authentication['expiry_timedeltas']['magic_link'])

    if authorization.exception:
        raise authorization.exception()

    with Session(c.db_engine) as session:

        token_lifespan = c.authentication['expiry_timedeltas']['access_token']
        user_access_token = await models.UserAccessToken.api_post(
            session=session, c=c,  authorized_user_id=authorization._user_id, admin=False, create_model=models.UserAccessTokenAdminCreate(
                user_id=authorization.user.id, lifespan=token_lifespan
            )
        )
        auth.set_access_token_cookie(response, c.jwt_encode(
            user_access_token.encode()), token_lifespan)

        # one time link, delete the auth_credential
        session.delete(authorization.auth_credential)
        session.commit()

        return PostLoginWithMagicLinkResponse(
            auth=GetAuthBaseReturn(
                user=models.UserPrivate.model_validate(authorization.user),
                scope_ids=set(
                    config.USER_ROLE_ID_SCOPE_IDS[authorization.user.user_role_id]),
                auth_credential=AuthCredentialIdTypeAndExpiry(
                    id=user_access_token.id, type='access_token', expiry=user_access_token.expiry)
            )
        )


class PostLoginWithOTPResponse(GetAuthReturn):
    pass


async def post_login_otp(session: Session, user: models.User, response: Response, code: models.OTPTypes.code) -> PostLoginWithOTPResponse:

    if not user:
        raise auth.invaliad_otp_exception()

    user_otps = user.otps
    found = False

    # the most recent ones are at the end
    for otp in user_otps[::-1]:
        if models.OTP.verify_code(code, otp.hashed_code):
            found = True
            break

    if not found:
        raise auth.invaliad_otp_exception()

    token_lifespan = c.authentication['expiry_timedeltas']['access_token']
    get_auth = await get_auth_from_auth_credential_table_inst(
        session, otp, override_lifetime=token_lifespan)

    if get_auth.exception:
        raise get_auth.exception()

    # if the code is active and correct, create an access token
    user_access_token = await models.UserAccessToken.api_post(
        session=session, c=c,  authorized_user_id=user._id, admin=False, create_model=models.UserAccessTokenAdminCreate(
            user_id=user._id, lifespan=token_lifespan
        )
    )
    auth.set_access_token_cookie(response, c.jwt_encode(
        user_access_token.encode()), token_lifespan
    )

    # one time link, delete the auth_credential
    session.delete(otp)
    session.commit()

    return PostLoginWithOTPResponse(
        auth=GetAuthBaseReturn(
            user=models.UserPrivate.model_validate(user),
            scope_ids=await user_access_token.get_scope_ids(session),
            auth_credential=AuthCredentialIdTypeAndExpiry(
                id=user_access_token._id, type='access_token', expiry=user_access_token.expiry)
        )
    )


class PostLoginWithOTPEmailRequest(BaseModel):
    code: models.OTPTypes.code
    email: models.UserTypes.email


@ auth_router.post('/login/otp/email/')
async def post_login_otp_email(
        model: PostLoginWithOTPEmailRequest,
        response: Response) -> PostLoginWithOTPResponse:

    with Session(c.db_engine) as session:
        user = session.exec(select(models.User).where(
            models.User.email == model.email)).one_or_none()
        return await post_login_otp(session, user, response, model.code)


class PostLoginWithOTPPhoneNumberRequest(BaseModel):
    code: models.OTPTypes.code
    phone_number: models.UserTypes.phone_number


@auth_router.post('/login/otp/phone_number/')
async def post_login_otp_phone_number(
    model: PostLoginWithOTPPhoneNumberRequest,
    response: Response
) -> PostLoginWithOTPResponse:

    with Session(c.db_engine) as session:
        user = session.exec(select(models.User).where(
            models.User.phone_number == model.phone_number)).one_or_none()
        return await post_login_otp(session, user, response, model.code)


class PostLoginWithGoogleRequest(BaseModel):
    access_token: str


class PostLoginWithGoogleResponse(GetAuthReturn):
    pass


@ auth_router.post("/login/google/", responses={status.HTTP_400_BAD_REQUEST: {'description': 'Invalid token', 'model': DetailOnlyResponse}})
async def post_login_google(request_token: PostLoginWithGoogleRequest, response: Response) -> PostLoginWithGoogleResponse:

    async with httpx.AsyncClient() as client:
        res = await client.get('https://www.googleapis.com/oauth2/v3/userinfo?access_token={}'.format(request_token.access_token))
        res.raise_for_status()
        user_info = res.json()

    # fields: sub, name, given_name, family_name, picture, email, email_verified
    email = user_info.get('email')
    if not email:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            detail='Invalid token')
    with Session(c.db_engine) as session:

        user = session.exec(select(models.User).where(
            models.User.email == email)).one_or_none()
        if not user:
            user = await models.User.api_post(session=session, c=c, authorized_user_id=None, admin=True, create_model=models.UserAdminCreate(email=email, user_role_id=config.USER_ROLE_NAME_MAPPING['user']))

        token_lifespan = c.authentication['expiry_timedeltas']['access_token']

        user_access_token = await models.UserAccessToken.api_post(
            session=session, c=c,  authorized_user_id=user._id,  admin=False, create_model=models.UserAccessTokenAdminCreate(
                user_id=user.id, lifespan=token_lifespan
            ))

        auth.set_access_token_cookie(response, c.jwt_encode(
            user_access_token.encode()), token_lifespan)

        return PostLoginWithGoogleResponse(
            auth=GetAuthBaseReturn(
                user=models.UserPrivate.model_validate(user),
                scope_ids=set(
                    config.USER_ROLE_ID_SCOPE_IDS[user.user_role_id]),
                auth_credential=AuthCredentialIdTypeAndExpiry(
                    id=user_access_token.id, type='access_token', expiry=user_access_token.expiry)
            )
        )


class PostSignUpRequest(BaseModel):
    token: str


class PostSignUpResponse(GetAuthReturn):
    pass


@auth_router.post('/signup/')
async def post_signup(response: Response, model: PostSignUpRequest) -> PostSignUpResponse:

    authorization = await get_auth_from_token(
        token=model.token,
        permitted_auth_credential_types={'sign_up'},
        override_lifetime=c.authentication['expiry_timedeltas']['request_sign_up'])

    with Session(c.db_engine) as session:
        sign_up: models.SignUp = authorization.auth_credential

        user_create_admin = models.UserAdminCreate(
            email=sign_up.email, user_role_id=config.USER_ROLE_NAME_MAPPING['user'])

        user = await models.User.api_post(session=session, c=c, authorized_user_id=None,
                                          admin=False, create_model=user_create_admin)

        token_lifespan = c.authentication['expiry_timedeltas']['access_token']
        user_access_token = await models.UserAccessToken.api_post(
            session=session, c=c,  authorized_user_id=user._id, admin=False, create_model=models.UserAccessTokenAdminCreate(
                user_id=user._id, type='access_token', lifespan=token_lifespan
            ))

        auth.set_access_token_cookie(response, c.jwt_encode(
            user_access_token.encode()), token_lifespan)

        return PostSignUpResponse(
            auth=GetAuthBaseReturn(
                user=models.UserPrivate.model_validate(user),
                scope_ids=set(
                    config.USER_ROLE_ID_SCOPE_IDS[user.user_role_id]),
                auth_credential=AuthCredentialIdTypeAndExpiry(
                    id=user_access_token.id, type='access_token', expiry=user_access_token.expiry)
            )
        )


async def send_signup_link(session: Session, user: models.User,  email: typing.Optional[models.UserTypes.email] = None, phone_number: typing.Optional[models.UserTypes.phone_number] = None):

    # existing user, send email to existing user
    if user:
        user_access_token = await models.UserAccessToken.api_post(
            session=session, c=c,  authorized_user_id=None, admin=True,
            create_model=models.UserAccessTokenAdminCreate(user_id=user._id, lifespan=c.authentication['expiry_timedeltas']['magic_link']))

        url = '{}{}/?token={}'.format(config.FRONTEND_URLS['base'],
                                      config.FRONTEND_URLS['verify_magic_link'], c.jwt_encode(user_access_token.encode()))

        if email:
            c.send_email(
                email, 'Sign Up Request', 'Somebody requested to sign up with this email. An account already exists with this email. Click here to login instead: {}'.format(url))
        if phone_number:
            c.send_sms(
                phone_number, 'Somebody requested to sign up with this phone number. An account already exists with this phone number. Click here to login instead: {}'.format(url))

    else:
        sign_up = models.SignUp.create(models.SignUpAdminCreate(
            email=email, lifespan=c.authentication['expiry_timedeltas']['request_sign_up']
        ))
        sign_up_jwt = c.jwt_encode(sign_up.encode())
        url = '{}{}/?token={}'.format(config.FRONTEND_URLS['base'],
                                      config.FRONTEND_URLS['verify_signup'], sign_up_jwt)

        if email:
            c.send_email(email, 'Sign Up',
                         'Click here to sign up: {}'.format(url))
        if phone_number:
            c.send_sms(phone_number, 'Click here to sign up: {}'.format(url))


class PostRequestSignUpEmailRequest(BaseModel):
    email: models.UserTypes.email


@ auth_router.post('/request/signup/email/')
async def post_request_sign_up_email(
    model: PostRequestSignUpEmailRequest,
    background_tasks: BackgroundTasks
):

    with Session(c.db_engine) as session:
        user = session.exec(select(models.User).where(
            models.User.email == model.email)).one_or_none()
        background_tasks.add_task(
            send_signup_link, session, user, email=model.email)
        return Response()


class PostRequestSignUpSMSRequest(BaseModel):
    phone_number: models.UserTypes.phone_number


@auth_router.post('/request/signup/sms/')
async def post_request_sign_up_sms(
    model: PostRequestSignUpSMSRequest,
    background_tasks: BackgroundTasks
):
    with Session(c.db_engine) as session:
        user = session.exec(select(models.User).where(
            models.User.phone_number == model.phone_number)).one_or_none()
        background_tasks.add_task(
            send_signup_link, session, user, phone_number=model.phone_number)
        return Response()


async def send_magic_link(session: Session, user: models.User, email: typing.Optional[models.UserTypes.email] = None, phone_number: typing.Optional[models.UserTypes.phone_number] = None):

    user_access_token = await models.UserAccessToken.api_post(
        session=session, c=c,  authorized_user_id=None, admin=True,
        create_model=models.UserAccessTokenAdminCreate(user_id=user._id, lifespan=c.authentication['expiry_timedeltas']['magic_link']))

    url = '{}{}/?token={}'.format(config.FRONTEND_URLS['base'],
                                  config.FRONTEND_URLS['verify_magic_link'], c.jwt_encode(user_access_token.encode()))

    if email:
        c.send_email(email, 'Magic Link', 'Click to login: {}'.format(url))
    if phone_number:
        c.send_sms(user.phone_number, 'Click to login: {}'.format(url))


class PostRequestMagicLinkEmailRequest(BaseModel):
    email: models.UserTypes.email


@ auth_router.post('/request/magic-link/email/')
async def post_request_magic_link_email(model: PostRequestMagicLinkEmailRequest, background_tasks: BackgroundTasks):

    with Session(c.db_engine) as session:
        user = session.exec(select(models.User).where(
            models.User.email == model.email)).one_or_none()
        if user:
            background_tasks.add_task(
                send_magic_link, session, user, email=model.email)
    return Response()


class PostRequestMagicLinkSMSRequest(BaseModel):
    phone_number: models.UserTypes.phone_number


@auth_router.post('/request/magic-link/sms/')
async def post_request_magic_link_sms(model: PostRequestMagicLinkSMSRequest, background_tasks: BackgroundTasks):
    with Session(c.db_engine) as session:
        user = session.exec(select(models.User).where(
            models.User.email == model.phone_number)).one_or_none()
        if user:
            background_tasks.add_task(
                send_magic_link, session, user, phone_number=model.phone_number)
    return Response()


async def send_otp(session: Session, user: models.User, email: typing.Optional[models.UserTypes.email] = None, phone_number: typing.Optional[models.UserTypes.phone_number] = None):

    code = models.OTP.generate_code()
    otp = await models.OTP.api_post(session=session, c=c, authorized_user_id=user._id, create_model=models.OTPAdminCreate(
        user_id=user._id, hashed_code=models.OTP.hash_code(code), lifespan=c.authentication['expiry_timedeltas']['otp']), admin=False)

    if email:
        c.send_email(email, 'OTP', 'Your OTP is: {}'.format(code))
    if phone_number:
        c.send_sms(phone_number, 'Your OTP is: {}'.format(code))


class PostRequestOTPEmailRequest(BaseModel):
    email: models.UserTypes.email


@ auth_router.post('/request/otp/email/')
async def post_request_otp_email(model: PostRequestOTPEmailRequest, background_tasks: BackgroundTasks):

    with Session(c.db_engine) as session:
        user = session.exec(select(models.User).where(
            models.User.email == model.email)).one_or_none()

        if user:
            background_tasks.add_task(
                send_otp, session, user, email=model.email)
    return Response()


class PostRequestOTPSMSRequest(BaseModel):
    phone_number: models.UserTypes.phone_number


@ auth_router.post('/request/otp/sms/')
async def post_request_otp_email(model: PostRequestOTPSMSRequest, background_tasks: BackgroundTasks):

    with Session(c.db_engine) as session:
        user = session.exec(select(models.User).where(
            models.User.phone_number == model.phone_number)).one_or_none()
        if user:
            background_tasks.add_task(
                send_otp, session, user, phone_number=model.phone_number)
    return Response()


@ auth_router.post('/logout/')
async def logout(response: Response, authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(raise_exceptions=False, permitted_auth_credential_types={'access_token'}))]) -> DetailOnlyResponse:

    if authorization.auth_credential:
        if authorization.auth_credential.auth_type == 'access_token':
            with Session(c.db_engine) as session:
                await models.UserAccessToken.api_delete(session=session, c=c, authorized_user_id=authorization._user_id, id=authorization.auth_credential.id, admin=False)

    auth.delete_access_token_cookie(response)
    return DetailOnlyResponse(detail='Logged out')

app.include_router(auth_router)


def get_pagination(max_limit: int = 100, default_limit: int = 10):
    def dependency(limit: int = Query(default_limit, ge=1, le=max_limit, description='Quantity of results'), offset: int = Query(0, ge=0, description='Index of the first result')):
        return models.Pagination(limit=limit, offset=offset)
    return dependency


# Users
user_router = APIRouter(
    prefix='/users', tags=[models.User._ROUTER_TAG])
user_admin_router = APIRouter(
    prefix='/admin/users', tags=[models.User._ROUTER_TAG, 'Admin'])


@ user_router.get('/me/', responses=models.User.get_responses())
async def get_user_me(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())]
) -> models.UserPrivate:
    return models.UserPrivate.model_validate(authorization.user)


@ user_router.get('/{user_id}/', responses=models.User.get_responses())
async def get_user_by_id(
    user_id: models.UserTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(raise_exceptions=False))]
) -> models.UserPublic:
    with Session(c.db_engine) as session:
        return models.UserPublic.model_validate(await models.User.api_get(session=session, c=c, authorized_user_id=authorization._user_id, id=user_id, admin=False))


@ user_admin_router.get('/{user_id}/', responses=models.User.get_responses())
async def get_user_by_id_admin(
    user_id: models.UserTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))]
) -> models.User:
    with Session(c.db_engine) as session:
        a = await models.User.api_get(session=session, c=c, authorized_user_id=authorization._user_id, id=user_id, admin=True)


@ user_admin_router.post('/', responses=models.User.post_responses())
async def post_user_admin(
    user_create_admin: models.UserAdminCreate,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))]
) -> models.User:
    with Session(c.db_engine) as session:
        return await models.User.api_post(session=session, c=c, authorized_user_id=authorization._user_id, admin=True, create_model=user_create_admin)


@ user_router.patch('/me/', responses=models.User.patch_responses())
async def patch_self(
    user_update: models.UserUpdate,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())]
) -> models.UserPrivate:
    with Session(c.db_engine) as session:
        return models.UserPrivate.model_validate(await models.User.api_patch(session=session, c=c, authorized_user_id=authorization._user_id, id=authorization._user_id, admin=False, update_model=models.UserAdminUpdate(**user_update.model_dump(exclude_unset=True))))


@ user_admin_router.patch('/{user_id}/', responses=models.User.patch_responses())
async def patch_user_admin(
    user_id: models.UserTypes.id,
    user_update_admin: models.UserAdminUpdate,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))]
) -> models.User:
    with Session(c.db_engine) as session:
        return await models.User.api_patch(session=session, c=c, authorized_user_id=authorization._user_id, id=user_id, admin=True, update_model=user_update_admin)


@ user_router.delete('/me/', responses=models.User.delete_responses(), status_code=status.HTTP_204_NO_CONTENT)
async def delete_self(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())]
):
    with Session(c.db_engine) as session:
        return await models.User.api_delete(session=session, c=c, authorized_user_id=authorization._user_id, id=authorization._user_id, admin=False)


@ user_admin_router.delete('/{user_id}/', responses=models.User.delete_responses(), status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_admin(
    user_id: models.UserTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))]
):
    with Session(c.db_engine) as session:
        return await models.User.api_delete(session=session, c=c, authorized_user_id=authorization._user_id, id=user_id, admin=True)


@ user_router.get('/', responses=models.User.post_responses())
async def get_users(
    pagination: typing.Annotated[models.Pagination, Depends(get_pagination())]
) -> list[models.UserPublic]:

    with Session(c.db_engine) as session:
        query = select(models.User).where(
            models.User.username != None)
        query = models.build_pagination(query, pagination)
        users = session.exec(query).all()
        return [models.UserPublic.model_validate(user) for user in users]


@ user_admin_router.get('/')
async def get_users_admin(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))],
    pagination: typing.Annotated[models.Pagination, Depends(get_pagination())]
) -> list[models.User]:

    with Session(c.db_engine) as session:
        query = select(models.User)
        query = models.build_pagination(query, pagination)
        users = session.exec(query).all()
        return users


@ user_router.get('/available/username/{username}/',
                  responses={status.HTTP_409_CONFLICT: {
                      "description": 'Username already exists', 'model': DetailOnlyResponse}})
async def get_user_username_available(username: models.UserTypes.username):
    with Session(c.db_engine) as session:
        return await models.User.api_get_is_username_available(session, username)


app.include_router(user_router)
app.include_router(user_admin_router)


# User Access Tokens

user_access_token_router = APIRouter(
    prefix='/user-access-tokens', tags=[models.UserAccessToken._ROUTER_TAG])
user_access_token_admin_router = APIRouter(
    prefix='/admin/user-access-tokens', tags=[models.UserAccessToken._ROUTER_TAG, 'Admin'])


@ user_access_token_router.get('/{user_access_token_id}/', responses=models.UserAccessToken.get_responses())
async def get_user_access_token_by_id(
    user_access_token_id: models.UserAccessTokenTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())]
) -> models.UserAccessToken:
    with Session(c.db_engine) as session:
        return await models.UserAccessToken.api_get(session=session, c=c, authorized_user_id=authorization._user_id, id=user_access_token_id, admin=False)


@ user_access_token_admin_router.get('/{user_access_token_id}/', responses=models.UserAccessToken.get_responses())
async def get_user_access_token_by_id_admin(
    user_access_token_id: models.UserAccessTokenTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))]
) -> models.UserAccessToken:
    with Session(c.db_engine) as session:
        return await models.UserAccessToken.api_get(session=session, c=c, authorized_user_id=authorization._user_id, id=user_access_token_id, admin=True)


@ user_access_token_admin_router.post('/', responses=models.UserAccessToken.post_responses())
async def post_user_access_token_admin(
    user_access_token_create_admin: models.UserAccessTokenAdminCreate,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))]
) -> models.UserAccessToken:
    with Session(c.db_engine) as session:
        return await models.UserAccessToken.api_post(session=session, c=c, authorized_user_id=authorization._user_id, admin=True, create_model=user_access_token_create_admin)


@ user_access_token_router.delete('/{user_access_token_id}/', responses=models.UserAccessToken.delete_responses(), status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_access_token(
    user_access_token_id: models.UserAccessTokenTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())]
):
    with Session(c.db_engine) as session:
        return await models.UserAccessToken.api_delete(session=session, c=c, authorized_user_id=authorization._user_id, id=user_access_token_id, admin=False)


@ user_access_token_admin_router.delete('/{user_access_token_id}/', responses=models.UserAccessToken.delete_responses(), status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_access_token_admin(
    user_access_token_id: models.UserAccessTokenTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))]
):
    with Session(c.db_engine) as session:
        return await models.UserAccessToken.api_delete(session=session, c=c, authorized_user_id=authorization._user_id, id=user_access_token_id, admin=True)


WrongUserPermissionUserAccessToken = HTTPException(
    status.HTTP_403_FORBIDDEN, detail='User does not have permission to view another user\'s access tokens')


def user_access_token_pagination(
    pagination: typing.Annotated[models.Pagination, Depends(
        get_pagination(default_limit=50, max_limit=500))]
):
    return pagination


@ user_access_token_router.get('/', tags=[models.User._ROUTER_TAG], responses={status.HTTP_404_NOT_FOUND: {"description": models.User.not_found_message(), 'model': NotFoundResponse}, WrongUserPermissionUserAccessToken.status_code: {'description': WrongUserPermissionUserAccessToken.detail, 'model': DetailOnlyResponse}})
async def get_user_access_tokens(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())],
    pagination: models.Pagination = Depends(user_access_token_pagination)

) -> list[models.UserAccessToken]:
    with Session(c.db_engine) as session:
        query = select(models.UserAccessToken).where(
            models.UserAccessToken.user_id == authorization._user_id)
        query = models.build_pagination(query, pagination)
        user_access_tokens = session.exec(query).all()
        return user_access_tokens


@ user_access_token_admin_router.get('/users/{user_id}/', tags=[models.User._ROUTER_TAG], responses={status.HTTP_404_NOT_FOUND: {"description": models.User.not_found_message(), 'model': NotFoundResponse}})
async def get_user_access_tokens_admin(
    user_id: models.UserTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))],
    pagination: models.Pagination = Depends(user_access_token_pagination)
) -> list[models.UserAccessToken]:
    with Session(c.db_engine) as session:

        query = select(models.UserAccessToken).where(
            models.UserAccessToken.user_id == user_id)
        query = models.build_pagination(query, pagination)
        user_access_tokens = session.exec(query).all()
        return user_access_tokens


@ user_access_token_router.get('/details/count/')
async def get_user_access_tokens_count(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())],
) -> int:
    with Session(c.db_engine) as session:
        query = select(func.count()).select_from(models.UserAccessToken).where(
            models.UserAccessToken.user_id == authorization._user_id)
        return session.exec(query).one()


app.include_router(user_access_token_router)
app.include_router(user_access_token_admin_router)


# API Keys


api_key_router = APIRouter(
    prefix='/api-keys', tags=[models.ApiKey._ROUTER_TAG])
api_key_admin_router = APIRouter(
    prefix='/admin/api-keys', tags=[models.ApiKey._ROUTER_TAG, 'Admin'])


@ api_key_router.get('/{api_key_id}/', responses=models.ApiKey.get_responses())
async def get_api_key_by_id(
    api_key_id: models.ApiKeyTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())]
) -> models.ApiKeyPrivate:
    with Session(c.db_engine) as session:
        return models.ApiKeyPrivate.model_validate(await models.ApiKey.api_get(session=session, c=c, authorized_user_id=authorization.user.id, id=api_key_id, admin=False))


@ api_key_admin_router.get('/{api_key_id}/', responses=models.ApiKey.get_responses())
async def get_api_key_by_id_admin(
    api_key_id: models.ApiKeyTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))]
) -> models.ApiKey:
    with Session(c.db_engine) as session:
        return await models.ApiKey.api_get(session=session, c=c, authorized_user_id=authorization.user.id, id=api_key_id, admin=True)


@ api_key_router.post('/', responses=models.ApiKey.post_responses())
async def post_api_key_to_user(
    api_key_create: models.ApiKeyCreate,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())]
) -> models.ApiKeyPrivate:

    with Session(c.db_engine) as session:
        return models.ApiKeyPrivate.from_api_key(await models.ApiKey.api_post(session=session, c=c, authorized_user_id=authorization._user_id, admin=False, create_model=models.ApiKeyAdminCreate(
            **api_key_create.model_dump(exclude_unset=True), user_id=authorization._user_id)))


@ api_key_admin_router.post('/', responses=models.ApiKey.post_responses())
async def post_api_key_to_user_admin(
    api_key_create_admin: models.ApiKeyAdminCreate,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))]
) -> models.ApiKey:
    with Session(c.db_engine) as session:
        return await models.ApiKey.api_post(session=session, c=c, authorized_user_id=authorization.user.id, admin=True, create_model=models.ApiKeyAdminCreate(**api_key_create_admin.model_dump(exclude_unset=True)))


@ api_key_router.patch('/{api_key_id}/', responses=models.ApiKey.patch_responses())
async def patch_api_key(
    api_key_id: models.ApiKeyTypes.id,
    api_key_update: models.ApiKeyUpdate,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())]
) -> models.ApiKeyPrivate:
    with Session(c.db_engine) as session:
        return models.ApiKeyPrivate.from_api_key(await models.ApiKey.api_patch(session=session, c=c, authorized_user_id=authorization.user.id, id=api_key_id, admin=False, update_model=models.ApiKeyAdminUpdate(**api_key_update.model_dump(exclude_unset=True))))


@ api_key_admin_router.patch('/{api_key_id}/', responses=models.ApiKey.patch_responses())
async def patch_api_key_admin(
    api_key_id: models.ApiKeyTypes.id,
    api_key_update_admin: models.ApiKeyAdminUpdate,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))]
) -> models.ApiKey:
    with Session(c.db_engine) as session:
        return await models.ApiKey.api_patch(session=session, c=c, authorized_user_id=authorization.user.id, id=api_key_id, admin=True, update_model=models.ApiKeyAdminUpdate(**api_key_update_admin.model_dump(exclude_unset=True)))


@ api_key_router.delete('/{api_key_id}/', responses=models.ApiKey.delete_responses(), status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    api_key_id: models.ApiKeyTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())]
):
    with Session(c.db_engine) as session:
        return await models.ApiKey.api_delete(session=session, c=c, authorized_user_id=authorization.user.id, id=api_key_id, admin=False)


@ api_key_admin_router.delete('/{api_key_id}/', responses=models.ApiKey.delete_responses(), status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key_admin(
    api_key_id: models.ApiKeyTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))]
):
    with Session(c.db_engine) as session:
        return await models.ApiKey.api_delete(session=session, c=c, authorized_user_id=authorization.user.id, id=api_key_id, admin=True)


class ApiKeyJWTResponse(BaseModel):
    jwt: str


@ api_key_router.get('/{api_key_id}/generate-jwt/', responses={status.HTTP_404_NOT_FOUND: {"description": models.ApiKey.not_found_message(), 'model': NotFoundResponse}})
async def get_api_key_jwt(
    api_key_id: models.ApiKeyTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())]
) -> ApiKeyJWTResponse:
    with Session(c.db_engine) as session:
        api_key = await models.ApiKey.api_get(session=session, c=c, authorized_user_id=authorization.user.id, id=api_key_id, admin=False)
        return ApiKeyJWTResponse(
            jwt=c.jwt_encode(api_key.encode())
        )

UserNotPermittedToViewAnotherUserApiKeys = HTTPException(
    status.HTTP_403_FORBIDDEN, detail='User does not have permission to view another user\'s API keys')


class GetApiKeysQueryParamsReturn(BaseModel):
    pagination: models.Pagination
    order_bys: list[models.OrderBy[models.ApiKeyTypes.order_by]]


def get_api_keys_query_params(
    pagination: typing.Annotated[models.Pagination, Depends(get_pagination())],
    order_bys: typing.Annotated[list[models.OrderBy[models.ApiKeyTypes.order_by]], Depends(
        models.ApiKey.get_order_by_depends())]
):
    return GetApiKeysQueryParamsReturn(pagination=pagination, order_bys=order_bys)


@ api_key_router.get('/')
async def get_user_api_keys(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())],
    get_api_keys_query_params: GetApiKeysQueryParamsReturn = Depends(
        get_api_keys_query_params)
) -> list[models.ApiKeyPrivate]:
    with Session(c.db_engine) as session:

        query = select(models.ApiKey).options(selectinload(models.ApiKey.api_key_scopes)).where(
            models.ApiKey.user_id == authorization._user_id)
        query = models.build_pagination(
            query, get_api_keys_query_params.pagination)
        query = models.ApiKey._build_order_by(
            query, get_api_keys_query_params.order_bys)

        user_api_keys = session.exec(query).all()
        return [models.ApiKeyPrivate.from_api_key(api_key) for api_key in user_api_keys]


@ api_key_router.get('/details/count/')
async def get_user_api_keys_count(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())],
) -> int:
    with Session(c.db_engine) as session:
        query = select(func.count()).select_from(models.ApiKey).where(
            models.ApiKey.user_id == authorization._user_id)
        return session.exec(query).one()


@ api_key_admin_router.get('/users/{user_id}/', tags=[models.User._ROUTER_TAG])
async def get_user_api_keys_admin(
    user_id: models.UserTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))],
    get_api_keys_query_params: GetApiKeysQueryParamsReturn = Depends(
        get_api_keys_query_params)
) -> list[models.ApiKey]:
    with Session(c.db_engine) as session:

        query = select(models.ApiKey).where(
            models.ApiKey.user_id == user_id)
        query = models.build_pagination(
            query, get_api_keys_query_params.pagination)
        query = models.ApiKey._build_order_by(
            query, get_api_keys_query_params.order_bys)

        user_api_keys = session.exec(query).all()
        return user_api_keys


@ api_key_router.get('/details/available/', responses={status.HTTP_409_CONFLICT: {"description": models.ApiKey.already_exists_message(), 'model': DetailOnlyResponse}})
async def get_api_key_available(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())],
    api_key_available: models.ApiKeyAvailable = Depends(),
):
    with Session(c.db_engine) as session:
        await models.ApiKey.api_get_is_available(session, models.ApiKeyAdminAvailable(
            **api_key_available.model_dump(exclude_unset=True), user_id=authorization.user.id
        ))


@ api_key_admin_router.get('/details/available/', responses={status.HTTP_409_CONFLICT: {"description": models.ApiKey.already_exists_message(), 'model': DetailOnlyResponse}})
async def get_api_key_available_admin(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))],
    api_key_available_admin: models.ApiKeyAdminAvailable = Depends(),
):
    with Session(c.db_engine) as session:
        await models.ApiKey.api_get_is_available(session, api_key_available_admin)


app.include_router(api_key_router)
app.include_router(api_key_admin_router)


# API Key Scope


api_key_scope_router = APIRouter(
    prefix='/api-key-scopes', tags=[models.ApiKeyScope._ROUTER_TAG])
api_key_scope_admin_router = APIRouter(
    prefix='/admin/api-key-scopes', tags=[models.ApiKeyScope._ROUTER_TAG, 'Admin'])


@ api_key_scope_router.post('/api-keys/{api_key_id}/scopes/{scope_id}/',
                            responses={status.HTTP_404_NOT_FOUND: {
                                "description": models.ApiKey.not_found_message(), 'model': NotFoundResponse}},
                            )
async def add_scope_to_api_key(
    api_key_id: models.ApiKeyTypes.id,
    scope_id: types.ScopeTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())]
):
    with Session(c.db_engine) as session:
        return await models.ApiKeyScope.api_post(session=session, c=c, authorized_user_id=authorization.user.id, create_model=models.ApiKeyScopeAdminCreate(api_key_id=api_key_id, scope_id=scope_id), admin=False)


@ api_key_scope_admin_router.post('/api-keys/{api_key_id}/scopes/{scope_id}/',
                                  responses={status.HTTP_404_NOT_FOUND: {
                                      "description": models.ApiKey.not_found_message(), 'model': NotFoundResponse}},
                                  )
async def add_scope_to_api_key_admin(
    api_key_id: models.ApiKeyTypes.id,
    scope_id: types.ScopeTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))]
):
    with Session(c.db_engine) as session:
        return await models.ApiKeyScope.api_post(session=session, c=c, authorized_user_id=authorization.user.id, create_model=models.ApiKeyScopeAdminCreate(api_key_id=api_key_id, scope_id=scope_id), admin=True)


@ api_key_scope_router.delete('/api-keys/{api_key_id}/scopes/{scope_id}/',
                              responses={status.HTTP_404_NOT_FOUND: {
                                  "description": models.ApiKey.not_found_message(), 'model': NotFoundResponse}},
                              status_code=status.HTTP_204_NO_CONTENT,
                              )
async def remove_scope_from_api_key(
    api_key_id: models.ApiKeyTypes.id,
    scope_id: types.ScopeTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())]
):
    with Session(c.db_engine) as session:
        return await models.ApiKeyScope.api_delete(session=session, c=c, authorized_user_id=authorization.user.id, id=models.ApiKeyScopeIdBase(api_key_id=api_key_id, scope_id=scope_id)._id, admin=False)


@ api_key_scope_admin_router.delete('/api-keys/{api_key_id}/scopes/{scope_id}/',
                                    responses={status.HTTP_404_NOT_FOUND: {
                                        "description": models.ApiKey.not_found_message(), 'model': NotFoundResponse}},
                                    status_code=status.HTTP_204_NO_CONTENT,
                                    )
async def remove_scope_from_api_key_admin(
    api_key_id: models.ApiKeyTypes.id,
    scope_id: types.ScopeTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))]
):
    with Session(c.db_engine) as session:
        return await models.ApiKeyScope.api_delete(session=session, c=c, authorized_user_id=authorization.user.id, id=models.ApiKeyScopeIdBase(api_key_id=api_key_id, scope_id=scope_id)._id, admin=True)

app.include_router(api_key_scope_router)
app.include_router(api_key_scope_admin_router)


# galleries


gallery_router = APIRouter(
    prefix='/galleries', tags=[models.Gallery._ROUTER_TAG])
gallery_admin_router = APIRouter(prefix='/admin/galleries', tags=[
    models.Gallery._ROUTER_TAG, 'Admin'])


@ gallery_router.get('/{gallery_id}/', responses=models.Gallery.get_responses())
async def get_gallery_by_id(
    gallery_id: models.GalleryTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(raise_exceptions=False))]
) -> models.GalleryPublic:
    with Session(c.db_engine) as session:
        return models.GalleryPublic.model_validate(await models.Gallery.api_get(session=session, c=c, authorized_user_id=authorization._user_id, id=gallery_id, admin=False))


@ gallery_admin_router.get('/{gallery_id}/', responses=models.Gallery.get_responses())
async def get_gallery_by_id_admin(
    gallery_id: models.GalleryTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))]
) -> models.Gallery:
    with Session(c.db_engine) as session:
        return await models.Gallery.api_get(session=session, c=c, authorized_user_id=authorization._user_id, id=gallery_id, admin=True)


@ gallery_router.post('/', responses=models.Gallery.post_responses())
async def post_gallery(
    gallery_create: models.GalleryCreate,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())]
) -> models.GalleryPrivate:
    with Session(c.db_engine) as session:
        return models.GalleryPrivate.model_validate(await models.Gallery.api_post(session=session, c=c, authorized_user_id=authorization._user_id, admin=False, create_model=models.GalleryAdminCreate(**gallery_create.model_dump(exclude_unset=True), user_id=authorization._user_id)))


@ gallery_admin_router.post('/', responses=models.Gallery.post_responses())
async def post_gallery_admin(
    gallery_create_admin: models.GalleryAdminCreate,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))]
) -> models.Gallery:
    with Session(c.db_engine) as session:
        return await models.Gallery.api_post(session=session, c=c, authorized_user_id=authorization._user_id, admin=True, create_model=models.GalleryAdminCreate(**gallery_create_admin.model_dump(exclude_unset=True)))


@ gallery_router.patch('/{gallery_id}/', responses=models.Gallery.patch_responses())
async def patch_gallery(
    gallery_id: models.GalleryTypes.id,
    gallery_update: models.GalleryUpdate,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())]
) -> models.GalleryPrivate:
    with Session(c.db_engine) as session:
        return models.GalleryPrivate.model_validate(await models.Gallery.api_patch(session=session, c=c, authorized_user_id=authorization._user_id, id=gallery_id, admin=False, update_model=models.GalleryAdminUpdate(**gallery_update.model_dump(exclude_unset=True))))


@ gallery_admin_router.patch('/{gallery_id}/', responses=models.Gallery.patch_responses())
async def patch_gallery_admin(
    gallery_id: models.GalleryTypes.id,
    gallery_update_admin: models.GalleryAdminUpdate,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))]
) -> models.Gallery:
    with Session(c.db_engine) as session:
        return await models.Gallery.api_patch(session=session, c=c, authorized_user_id=authorization._user_id, id=gallery_id, admin=True, update_model=models.GalleryAdminUpdate(**gallery_update_admin.model_dump(exclude_unset=True)))


@ gallery_router.delete('/{gallery_id}/', responses=models.Gallery.delete_responses(), status_code=status.HTTP_204_NO_CONTENT)
async def delete_gallery(
    gallery_id: models.GalleryTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())]
):
    with Session(c.db_engine) as session:
        return await models.Gallery.api_delete(session=session, c=c, authorized_user_id=authorization._user_id, id=gallery_id, admin=False)


@ gallery_admin_router.delete('/{gallery_id}/', responses=models.Gallery.delete_responses(), status_code=status.HTTP_204_NO_CONTENT)
async def delete_gallery_admin(
    gallery_id: models.GalleryTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))]
):
    with Session(c.db_engine) as session:
        return await models.Gallery.api_delete(session=session, c=c, authorized_user_id=authorization._user_id, id=gallery_id, admin=True)


@ gallery_router.get('/details/available/')
async def get_gallery_available(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())],
    gallery_available: models.GalleryAvailable = Depends(),
):
    with Session(c.db_engine) as session:
        await models.Gallery.api_get_is_available(session, models.GalleryAdminAvailable(
            **gallery_available.model_dump(exclude_unset=True), user_id=authorization.user.id
        ))


@ gallery_admin_router.get('/details/available/')
async def get_gallery_available_admin(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))],
    gallery_available_admin: models.GalleryAdminAvailable = Depends(),
):
    with Session(c.db_engine) as session:
        await models.Gallery.api_get_is_available(session, gallery_available_admin)


@ gallery_router.get('/')
async def get_galleries(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())],
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> list[models.GalleryPrivate]:

    with Session(c.db_engine) as session:
        galleries = session.exec(select(models.Gallery).where(
            models.Gallery.user_id == authorization._user_id).offset(offset).limit(limit)).all()
        return [models.GalleryPrivate.model_validate(gallery) for gallery in galleries]


# need to decide how to deal with gallery permissions and how to return

# @gallery_router.get('/users/{user_id}/', tags=[models.User._ROUTER_TAG])
# async def get_galleries_by_user(
#     user_id: models.UserTypes.id,
#     authorization: typing.Annotated[GetAuthorizationReturn, Depends(
#         get_auth_from_token(raise_exceptions=False))],
#     pagination: PaginationParams = Depends(get_pagination_params),
# ) -> list[models.GalleryPublic]:

#     with Session(c.db_engine) as session:
#         galleries = session.exec(select(models.Gallery).where(
#             models.Gallery.user_id == user_id).offset(pagination.offset).limit(pagination.limit)).all()
#         return [models.GalleryPublic.model_validate(gallery) for gallery in galleries]


@ gallery_admin_router.get('/users/{user_id}', tags=[models.User._ROUTER_TAG])
async def get_galleries_by_user_admin(
    user_id: models.UserTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(required_scopes={'admin'}))],
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> list[models.Gallery]:

    with Session(c.db_engine) as session:
        galleries = session.exec(select(models.Gallery).where(
            models.Gallery.user_id == user_id).offset(offset).limit(limit)).all()
        return galleries


class UploadFileToGalleryResponse(BaseModel):
    message: str


@ gallery_router.post("/{gallery_id}/upload/", status_code=status.HTTP_201_CREATED)
async def upload_file_to_gallery(
    gallery_id: models.GalleryTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())],
    file: UploadFile = File(...)
) -> UploadFileToGalleryResponse:

    # with Session(c.db_engine) as session:
    #     gallery = await models.Gallery.get(session, gallery_id)
    #     if not gallery:
    #         raise HTTPException(status.HTTP_404_NOT_FOUND,
    #                             detail=models.Gallery.not_found_message())

    #     gallery_permission = await models.GalleryPermission.GalleryPermissionModel.get(
    #         session, (gallery_id, authorization.user.id))

    #     if not gallery_permission:
    #         raise HTTPException(status.HTTP_404_NOT_FOUND,
    #                             detail=models.Gallery.not_found_message())
    #     if gallery_permission.permission_level < c.permission_level_name_mapping['editor']:
    #         raise HTTPException(status.HTTP_403_FORBIDDEN,
    #                             detail='User does not have permission to add files to this gallery')

    #     print(file.__dict__)
    #     file_path = gallery.get_dir(c.galleries_dir) / file.filename
    #     with open(file_path, "wb") as buffer:
    #         shutil.copyfileobj(file.file, buffer)

    return UploadFileToGalleryResponse(message="Files uploaded successfully")


@ gallery_router.post('/{gallery_id}/sync/')
async def sync_gallery(
    gallery_id: models.GalleryTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())]
) -> DetailOnlyResponse:

    with Session(c.db_engine) as session:
        gallery = await models.Gallery.api_get(session=session, c=c, authorized_user_id=authorization.user.id, id=gallery_id, admin=False)
        dir = await gallery.get_dir(session, c.galleries_dir)
        await gallery.sync_with_local(session, c, dir)
        return DetailOnlyResponse(detail='Synced gallery')

app.include_router(gallery_router)
app.include_router(gallery_admin_router)


# Pages


pages_router = APIRouter(prefix='/pages', tags=['Page'])


class GetProfilePageResponse(GetAuthReturn):
    user: models.UserPrivate | None = None


@ pages_router.get('/profile/', tags=[models.User._ROUTER_TAG])
async def get_pages_profile(authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency())]) -> GetProfilePageResponse:

    return GetProfilePageResponse(
        **get_auth(authorization).model_dump(),
        user=models.UserPrivate.model_validate(authorization.user)
    )


class GetHomePageResponse(GetAuthReturn):
    pass


@ pages_router.get('/home/')
async def get_home_page(authorization: typing.Annotated[GetAuthorizationReturn, Depends(make_get_auth_dependency(raise_exceptions=False))]) -> GetHomePageResponse:
    return GetHomePageResponse(
        **get_auth(authorization).model_dump()
    )


class GetSettingsPageResponse(GetAuthReturn):
    pass


@ pages_router.get('/settings/')
async def get_settings_page(
        authorization: typing.Annotated[GetAuthorizationReturn, Depends(
            make_get_auth_dependency(raise_exceptions=False))]
) -> GetSettingsPageResponse:
    return GetSettingsPageResponse(
        **get_auth(authorization).model_dump()
    )


class GetSettingsApiKeysPageResponse(GetAuthReturn):
    api_key_count: int
    api_keys: list[models.ApiKeyPrivate]


@ pages_router.get('/settings/api-keys/', tags=[models.ApiKey._ROUTER_TAG])
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
    user_access_tokens: list[models.UserAccessToken]


@ pages_router.get('/settings/user-access-tokens/', tags=[models.UserAccessToken._ROUTER_TAG])
async def get_settings_user_access_tokens_page(
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(make_get_auth_dependency())],
    pagination: models.Pagination = Depends(user_access_token_pagination)
) -> GetSettingsUserAccessTokensPageResponse:
    return GetSettingsUserAccessTokensPageResponse(
        **get_auth(authorization).model_dump(),
        user_access_token_count=await get_user_access_tokens_count(authorization),
        user_access_tokens=await get_user_access_tokens(authorization, pagination)
    )


class GetStylesPageResponse(GetAuthReturn):
    pass


@ pages_router.get('/styles/')
async def get_styles_page(authorization: typing.Annotated[GetAuthorizationReturn, Depends(make_get_auth_dependency(raise_exceptions=False))]) -> GetStylesPageResponse:
    return GetStylesPageResponse(
        **get_auth(authorization).model_dump()
    )


class GetGalleryPageResponse(GetAuthReturn):
    gallery: models.GalleryPublic
    parents: list[models.GalleryPublic]
    children: list[models.GalleryPublic]


@ pages_router.get('/galleries/{gallery_id}/', responses={status.HTTP_404_NOT_FOUND: {"description": models.Gallery.not_found_message(), 'model': NotFoundResponse}}, tags=[models.Gallery._ROUTER_TAG])
async def get_gallery_page(
    gallery_id: models.GalleryTypes.id,
    authorization: typing.Annotated[GetAuthorizationReturn, Depends(
        make_get_auth_dependency(raise_exceptions=False))],
    root: bool = Query(False),
) -> GetGalleryPageResponse:

    if root:
        with Session(c.db_engine) as session:
            if not authorization.isAuthorized:
                raise HTTPException(status.HTTP_404_NOT_FOUND,
                                    detail=models.Gallery.not_found_message())

            gallery = await models.Gallery.get_root_gallery(session, authorization.user.id)
            gallery_id = gallery._id

    with Session(c.db_engine) as session:
        gallery = await models.Gallery.api_get(
            session=session, c=c,  authorized_user_id=None if not authorization.isAuthorized else authorization.user.id, id=gallery_id, admin=False)

        return GetGalleryPageResponse(
            **get_auth(authorization).model_dump(),
            gallery=models.GalleryPublic.model_validate(gallery),
            parents=[models.GalleryPublic.model_validate(
                parent) for parent in await gallery.get_parents(session)],
            children=[models.GalleryPublic.model_validate(
                child) for child in gallery.children]
        )


# add the non admin routers first
app.include_router(pages_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
