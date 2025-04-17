from fastapi import Depends, Request
from fastapi.security import OAuth2, OAuth2PasswordRequestForm, OAuth2PasswordBearer, APIKeyHeader
from fastapi.openapi.models import OAuthFlowPassword
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession


from pydantic import BaseModel
import typing
from typing import Annotated
from fastapi import Request, HTTPException, status, Response
import datetime as datetime_module
from .. import client, types, auth
from ..auth import exceptions
from ..config import settings
from ..models import user as user_model_module, user_access_token as user_access_token_model_module, sign_up as sign_up_model_module, otp as otp_model_module
from ..models.bases import auth_credential
from .. import models


def set_access_token_cookie(response: Response, access_token: types.JwtEncodedStr,  expiry: datetime_module.datetime | None = None):

    kwargs = {}
    if expiry:
        kwargs['expires'] = expiry

    response.set_cookie(
        key=auth.ACCESS_TOKEN_COOKIE_KEY,
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        **kwargs
    )


def delete_access_token_cookie(response: Response):
    response.delete_cookie(auth.ACCESS_TOKEN_COOKIE_KEY)


class OAuth2PasswordBearerMultiSource(OAuth2):
    def __init__(
        self,
        flows: OAuthFlowsModel
    ):
        super().__init__(flows=flows, auto_error=False)

    async def __call__(self, request: Request) -> types.JwtEncodedStr | None:
        token: types.JwtEncodedStr | None = None
        provided_auth_types = set()

        # Authorization: bearer <token>
        authorization = request.headers.get("Authorization")
        if authorization:
            scheme, param = get_authorization_scheme_param(authorization)
            if scheme.lower() == "bearer":
                token = param
                provided_auth_types.add("bearer")

        # HTTP-only Cookie
        cookie_access_token = request.cookies.get(auth.ACCESS_TOKEN_COOKIE_KEY)
        if cookie_access_token:
            token = cookie_access_token
            provided_auth_types.add("cookie")

        if len(provided_auth_types) > 1:
            raise exceptions.Base(
                exceptions.multiple_authorization_types_provided(
                    provided_auth_types), logout=False
            )

        return token


oauth2_scheme = OAuth2PasswordBearerMultiSource(
    flows=OAuthFlowsModel(password=OAuthFlowPassword(tokenUrl="auth/token/")))


class GetAuthReturn(BaseModel):
    isAuthorized: bool = False
    exception: typing.Optional[exceptions.StatusCodeAndDetail] = None
    user: typing.Optional[user_model_module.UserPrivate] = None
    scope_ids: typing.Optional[set[types.Scope.id]] = None
    auth_credential: typing.Optional[models.AuthCredentialClassInstance] = None

    @property
    def _user_id(self):
        if self.auth_credential:
            if isinstance(self.auth_credential, auth_credential.Table):
                if self.auth_credential.user:
                    return self.auth_credential.user.id
        return None


class _BaseKwargs(typing.TypedDict):
    c: client.Client
    required_scopes: typing.NotRequired[set[types.Scope.name]]
    override_lifetime: typing.NotRequired[datetime_module.timedelta]


class _MakeGetAuthDepedencyAndGetAuthFromJwtKwargs(_BaseKwargs):
    permitted_types: typing.NotRequired[set[types.AuthCredential.type]]


class _GetAuthFromJwtAndGetAuthFromTableKwargs(_BaseKwargs):
    pass


class MakeGetAuthDepedencyKwargs(_MakeGetAuthDepedencyAndGetAuthFromJwtKwargs):
    raise_exceptions: typing.NotRequired[bool]
    logout_on_exception: typing.NotRequired[bool]


class GetAuthFromTableKwargs(_GetAuthFromJwtAndGetAuthFromTableKwargs):
    auth_credential_table_instance: models.AuthCredentialTableClassInstance
    dt_now: typing.NotRequired[datetime_module.datetime]
    read_from_db: typing.NotRequired[bool]


class GetAuthFromJwtKwargs(_MakeGetAuthDepedencyAndGetAuthFromJwtKwargs, _GetAuthFromJwtAndGetAuthFromTableKwargs):
    c: client.Client
    token: typing.Optional[types.JwtEncodedStr]


async def get_auth_from_auth_credential_table_inst(
        **kwargs: typing.Unpack[GetAuthFromTableKwargs]
) -> GetAuthReturn:

    c = kwargs.get('c')
    auth_credential_table_inst = kwargs.get('auth_credential_table_instance')
    required_scopes = kwargs.get('required_scopes', set())
    override_lifetime = kwargs.get('override_lifetime', None)
    dt_now = kwargs.get(
        'dt_now', datetime_module.datetime.now(datetime_module.UTC))
    read_from_db = kwargs.get('read_from_db', True)

    async with c.AsyncSession() as session:

        if read_from_db:
            auth_credential_from_db = await auth_credential_table_inst.read(
                {
                    'session': session,
                    'authorized_user_id': auth_credential_table_inst.user_id,
                    'c': c,
                    'id': auth_credential_table_inst.id,
                }
            )
        else:
            auth_credential_from_db = auth_credential_table_inst

        if not auth_credential_from_db:
            return GetAuthReturn(exception=exceptions.authorization_expired())

        # if it expired, delete it
        if dt_now > auth_credential_from_db.expiry:
            await session.delete(auth_credential_from_db)
            await session.commit()
            return GetAuthReturn(exception=exceptions.authorization_expired())

        if override_lifetime != None:
            if dt_now > (auth_credential_from_db.issued + override_lifetime):
                await session.delete(auth_credential_from_db)
                await session.commit()
                return GetAuthReturn(exception=exceptions.authorization_expired())

        # if no user is associated with the auth_credential, raise an exception
        user = auth_credential_from_db.user
        if user == None:
            return GetAuthReturn(exception=exceptions.user_not_found())

        scope_ids = set(await auth_credential_from_db.get_scope_ids(session))

        required_scope_ids = set(
            [settings.SCOPE_NAME_MAPPING[scope_name]
                for scope_name in required_scopes]
        )
        if not required_scope_ids.issubset(scope_ids):
            return GetAuthReturn(exception=exceptions.not_permitted())

        return GetAuthReturn(
            isAuthorized=True,
            user=user_model_module.UserPrivate.model_validate(user),
            scope_ids=scope_ids,
            auth_credential=auth_credential_from_db
        )


async def get_auth_from_auth_credential_jwt(**kwargs: typing.Unpack[GetAuthFromJwtKwargs]) -> GetAuthReturn:

    c = kwargs.get('c')
    token = kwargs.get('token', None)
    required_scopes = kwargs.get('required_scopes', set())
    permitted_types = kwargs.get('permitted_types', set(
        [c.auth_type for c in models.AUTH_CREDENTIAL_JWT_CLASSES]))
    override_lifetime = kwargs.get('override_lifetime', None)

    if token is None:
        return GetAuthReturn(exception=exceptions.missing_authorization())

    # make sure the token is a valid jwt
    try:
        payload: dict = c.jwt_decode(token)
    except:
        return GetAuthReturn(exception=exceptions.improper_format())

    # make sure "type" is in the jwt
    if auth_credential.JwtIO._TYPE_CLAIM not in payload:
        return GetAuthReturn(exception=exceptions.missing_required_claims({'jwt'}))

    # make sure the "type" is a permitted auth_credential type
    auth_type: models.AuthCredentialJwtType = payload['type']
    if auth_type not in permitted_types:
        return GetAuthReturn(exception=exceptions.authorization_type_not_permitted())

    AuthCredentialClass = models.AUTH_CREDENTIAL_TYPE_TO_CLASS[auth_type]

    # turn the payload into an AuthCredential instance
    try:
        auth_credential_inst_from_jwt = AuthCredentialClass.from_payload(
            payload)  # type: ignore
    except auth_credential.MissingRequiredClaimsError as e:
        return GetAuthReturn(exception=exceptions.missing_required_claims(set(e.claims)))
    except Exception:
        raise

    dt_now = datetime_module.datetime.now(datetime_module.UTC)

    # check the dates from the jwt
    if dt_now > auth_credential_inst_from_jwt.expiry:
        return GetAuthReturn(exception=exceptions.authorization_expired())
    if override_lifetime is not None:
        if dt_now > auth_credential_inst_from_jwt.issued + override_lifetime:
            return GetAuthReturn(exception=exceptions.authorization_expired())

    # if the auth_credential is also stored in the table, it will need to be in the db
    # for example, SignUp is a JWT only credential, so it will not be in the db
    # API keys are in the db, so it will be in the db
    if isinstance(auth_credential_inst_from_jwt, auth_credential.Table):

        get_auth_from_table_kwargs: GetAuthFromTableKwargs = {
            'c': c,
            'auth_credential_table_instance': typing.cast(
                models.AuthCredentialTableClassInstance, auth_credential_inst_from_jwt),
            'dt_now': dt_now,
        }

        if required_scopes:
            get_auth_from_table_kwargs['required_scopes'] = required_scopes
        if override_lifetime:
            get_auth_from_table_kwargs['override_lifetime'] = override_lifetime

        return await get_auth_from_auth_credential_table_inst(**get_auth_from_table_kwargs)

    else:
        # non-table auth_credentials have no scopes
        if required_scopes:
            return GetAuthReturn(exception=exceptions.not_permitted())

        return GetAuthReturn(
            isAuthorized=True,
            user=None,
            scope_ids=set(),
            auth_credential=auth_credential_inst_from_jwt
        )


def make_get_auth_dependency(**kwargs: typing.Unpack[MakeGetAuthDepedencyKwargs]):

    raise_exceptions = kwargs.get('raise_exceptions', True)
    logout_on_exception = kwargs.get('logout_on_exception', True)

    async def get_authorization_dependency(response: Response, auth_token: typing.Annotated[types.JwtEncodedStr | None, Depends(oauth2_scheme)]) -> GetAuthReturn:
        get_authorization_return = await get_auth_from_auth_credential_jwt(token=auth_token, **kwargs)
        if get_authorization_return.exception:
            if raise_exceptions:
                raise exceptions.Base(
                    get_authorization_return.exception, logout=logout_on_exception
                )
        return get_authorization_return
    return get_authorization_dependency


class GetUserSessionInfoReturn(BaseModel):
    user: typing.Optional[user_model_module.UserPrivate]
    scope_ids: typing.Optional[set[types.Scope.id]]
    access_token: typing.Optional[user_access_token_model_module.UserAccessTokenPublic]


assert settings.SHARED_CONSTANTS['auth_key'] == 'auth'


class GetUserSessionInfoNestedReturn(BaseModel):
    auth: GetUserSessionInfoReturn


def get_user_session_info(get_authorization_return: GetAuthReturn) -> GetUserSessionInfoNestedReturn:

    access_token: typing.Optional[user_access_token_model_module.UserAccessTokenPublic] = None
    if get_authorization_return.auth_credential and isinstance(get_authorization_return.auth_credential, user_access_token_model_module.UserAccessToken):
        access_token = user_access_token_model_module.UserAccessTokenPublic(
            id=get_authorization_return.auth_credential.id,
            expiry=get_authorization_return.auth_credential.expiry
        )

    return GetUserSessionInfoNestedReturn(auth=GetUserSessionInfoReturn(
        user=get_authorization_return.user,
        scope_ids=get_authorization_return.scope_ids,
        access_token=access_token
    ))


class DetailOnlyResponse(BaseModel):
    detail: str


class NotFoundResponse(DetailOnlyResponse):
    pass


def make_authenticate_user_with_username_and_password_dependency(c: client.Client):
    async def authenticate_user_with_username_and_password(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> user_model_module.User:

        async with c.AsyncSession() as session:
            user = await user_model_module.User.authenticate(
                session, form_data.username, form_data.password)
            if user is None:
                raise exceptions.Base(exceptions.credentials())
            return user

    return authenticate_user_with_username_and_password


async def send_signup_link(session: AsyncSession, c: client.Client, user: user_model_module.User,  email: typing.Optional[types.User.email] = None, phone_number: typing.Optional[types.User.phone_number] = None):

    # existing user, send email to existing user
    if user:
        user_access_token = await user_access_token_model_module.UserAccessToken.create({
            'authorized_user_id': user.id,
            'session': session,
            'c': c,
            'create_model': user_access_token_model_module.UserAccessTokenAdminCreate(
                user_id=user.id,
                expiry=auth_credential.lifespan_to_expiry(
                    c.auth['credential_lifespans']['request_sign_up'])
            )
        })

        url = '{}{}/?token={}'.format(settings.FRONTEND_URLS['base'],
                                      settings.FRONTEND_URLS['verify_magic_link'], c.jwt_encode(typing.cast(dict, user_access_token.to_payload())))

        if email:
            c.send_email(
                email, 'Sign Up Request', 'Somebody requested to sign up with this email. An account already exists with this email. Click here to login instead: {}'.format(url))
        if phone_number:
            c.send_sms(
                phone_number, 'Somebody requested to sign up with this phone number. An account already exists with this phone number. Click here to login instead: {}'.format(url))

    else:

        sign_up = sign_up_model_module.SignUp.create(sign_up_model_module.SignUpAdminCreate(
            email=email, lifespan=c.auth['credential_lifespans']['request_sign_up']
        ))
        sign_up_jwt = c.jwt_encode(typing.cast(dict, sign_up.to_payload()))
        url = '{}{}/?token={}'.format(settings.FRONTEND_URLS['base'],
                                      settings.FRONTEND_URLS['verify_signup'], sign_up_jwt)

        if email:
            c.send_email(email, 'Sign Up',
                         'Click here to sign up: {}'.format(url))
        if phone_number:
            c.send_sms(
                phone_number, 'Click here to sign up: {}'.format(url))


class PostLoginWithOTPResponse(GetUserSessionInfoNestedReturn):
    pass


async def post_login_otp(session: AsyncSession, c: client.Client, user: user_model_module.User, response: Response, code: types.OTP.code) -> PostLoginWithOTPResponse:

    if user is None:
        raise exceptions.Base(exceptions.invalid_otp())

    user_otps = user.otps

    # the most recent ones are at the end
    otp: otp_model_module.OTP | None = None
    for otp in user_otps[::-1]:
        if otp_model_module.OTP.verify_code(code, otp.hashed_code):
            break

    if otp is None:
        raise exceptions.Base(exceptions.invalid_otp())

    get_auth = await get_auth_from_auth_credential_table_inst(
        c=c,
        auth_credential_table_instance=otp,
        read_from_db=False,
        override_lifetime=c.auth['credential_lifespans']['access_token']
    )

    if get_auth.exception:
        raise exceptions.Base(get_auth.exception)

    # if the code is active and correct, create a new access token
    user_access_token = await user_access_token_model_module.UserAccessToken.create({
        'authorized_user_id': user.id,
        "c": c,
        'session': session,
        'create_model': user_access_token_model_module.UserAccessTokenAdminCreate(
            user_id=user.id,
            expiry=auth_credential.lifespan_to_expiry(
                c.auth['credential_lifespans']['access_token']),
        )
    })

    set_access_token_cookie(response, c.jwt_encode(typing.cast(
        dict, user_access_token.to_payload())), expiry=user_access_token.expiry)

    # one time link, delete the auth_credential
    await session.delete(otp)
    await session.commit()

    return PostLoginWithOTPResponse(
        auth=GetUserSessionInfoReturn(
            user=user_model_module.UserPrivate.model_validate(user),
            scope_ids=set(await user_access_token.get_scope_ids(session)),
            access_token=user_access_token_model_module.UserAccessTokenPublic.model_validate(
                user_access_token)
        )
    )


async def send_magic_link(session: AsyncSession, c: client.Client, user: user_model_module.User, email: typing.Optional[types.User.email] = None, phone_number: typing.Optional[types.User.phone_number] = None):

    user_access_token = await user_access_token_model_module.UserAccessToken.create(
        {
            'authorized_user_id': user.id,
            'c': c,
            'session': session,
            'create_model': user_access_token_model_module.UserAccessTokenAdminCreate(user_id=user.id, expiry=auth_credential.lifespan_to_expiry(c.auth['credential_lifespans']['magic_link']))
        }
    )

    url = '{}{}/?token={}'.format(settings.FRONTEND_URLS['base'],
                                  settings.FRONTEND_URLS['verify_magic_link'], c.jwt_encode(typing.cast(dict, user_access_token.to_payload())))

    if email:
        c.send_email(email, 'Magic Link',
                     'Click to login: {}'.format(url))
    if phone_number:
        if user.phone_number:
            c.send_sms(user.phone_number, 'Click to login: {}'.format(url))


async def send_otp(session: AsyncSession, c: client.Client, user: user_model_module.User, email: typing.Optional[types.User.email] = None, phone_number: typing.Optional[types.User.phone_number] = None):

    code = otp_model_module.OTP.generate_code()
    otp = await otp_model_module.OTP.create({
        'authorized_user_id': user.id,
        'c': c,
        'session': session,
        'create_model': otp_model_module.OTPAdminCreate(
            user_id=user.id, hashed_code=otp_model_module.OTP.hash_code(code), expiry=auth_credential.lifespan_to_expiry(c.auth['credential_lifespans']['otp'])
        )
    })

    if email:
        c.send_email(email, 'OTP', 'Your OTP is: {}'.format(code))
    if phone_number:
        c.send_sms(phone_number, 'Your OTP is: {}'.format(code))
