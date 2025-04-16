from fastapi import Depends, Request
from fastapi.security import OAuth2, OAuth2PasswordRequestForm, OAuth2PasswordBearer, APIKeyHeader
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession


from pydantic import BaseModel
import typing
from typing import Annotated
from fastapi import Request, HTTPException, status, Response
import datetime
from .. import client, types, auth
from ..auth import exceptions
from ..config import settings
from ..models import user as user_model_module, user_access_token as user_access_token_model_module, sign_up as sign_up_model_module
from ..models.bases import auth_credential
from .. import models


def set_access_token_cookie(response: Response, access_token: types.JwtEncodedStr,  lifespan: datetime.timedelta | None):

    kwargs = {}
    if lifespan:
        kwargs['expires'] = datetime.datetime.now(
            datetime.UTC) + lifespan

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


def make_authenticate_user_with_username_and_password_dependency(c: client.Client):
    async def authenticate_user_with_username_and_password(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> models.User:

        async with c.AsyncSession() as session:
            user = await models.User.authenticate(
                session, form_data.username, form_data.password)
            if not user:
                raise exceptions.Base(exceptions.credentials())
            return user

    return authenticate_user_with_username_and_password


async def send_signup_link(session: AsyncSession, c: client.Client, user: models.User,  email: typing.Optional[types.User.email] = None, phone_number: typing.Optional[types.User.phone_number] = None):

    # existing user, send email to existing user
    if user:
        user_access_token = await models.UserAccessToken.create({
            'admin': True,
            'session': session,
            'c': c,
            'create_model': user_access_token_model_module.UserAccessTokenAdminCreate(
                user_id=user.id,
                expiry=auth_credential.lifespan_to_expiry(
                    c.auth['credential_lifespans']['request_sign_up'])
            )
        })

        url = '{}{}/?token={}'.format(settings.FRONTEND_URLS['base'],
                                      settings.FRONTEND_URLS['verify_magic_link'], c.jwt_encode(user_access_token.encode_model()))

        if email:
            c.send_email(
                email, 'Sign Up Request', 'Somebody requested to sign up with this email. An account already exists with this email. Click here to login instead: {}'.format(url))
        if phone_number:
            c.send_sms(
                phone_number, 'Somebody requested to sign up with this phone number. An account already exists with this phone number. Click here to login instead: {}'.format(url))

    else:
        sign_up = models.SignUp.create(models.SignUpAdminCreate(
            email=email, lifespan=c.auth['credential_lifespans']['request_sign_up']
        ))
        sign_up_jwt = c.jwt_encode(sign_up.encode())
        url = '{}{}/?token={}'.format(settings.FRONTEND_URLS['base'],
                                      settings.FRONTEND_URLS['verify_signup'], sign_up_jwt)

        if email:
            c.send_email(email, 'Sign Up',
                         'Click here to sign up: {}'.format(url))
        if phone_number:
            c.send_sms(
                phone_number, 'Click here to sign up: {}'.format(url))


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

    token_lifespan = c.auth['credential_lifespans']['access_token']
    get_auth = await get_auth_from_auth_credential_table_inst(
        session, otp, override_lifetime=token_lifespan)

    if get_auth.exception:
        raise get_auth.exception()

    # if the code is active and correct, create an access token
    user_access_token = await models.UserAccessToken.api_post(models.UserAccessToken.PostParams.model_construct(
        session=session, c=c,  authorized_user_id=user._id, create_model=models.UserAccessTokenAdminCreate(
            user_id=user._id, lifespan=token_lifespan
        )))

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


async def send_magic_link(session: Session, user: models.User, email: typing.Optional[models.UserTypes.email] = None, phone_number: typing.Optional[models.UserTypes.phone_number] = None):

    user_access_token = await models.UserAccessToken.api_post(models.UserAccessToken.PostParams.model_construct(session=session, c=c,  authorized_user_id=None, admin=True,
                                                                                                                create_model=models.UserAccessTokenAdminCreate(user_id=user._id, lifespan=c.auth['credential_lifespans']['magic_link']))
                                                              )

    url = '{}{}/?token={}'.format(settings.FRONTEND_URLS['base'],
                                  settings.FRONTEND_URLS['verify_magic_link'], c.jwt_encode(user_access_token.encode()))

    if email:
        c.send_email(email, 'Magic Link',
                     'Click to login: {}'.format(url))
    if phone_number:
        c.send_sms(user.phone_number, 'Click to login: {}'.format(url))


async def send_otp(session: Session, user: models.User, email: typing.Optional[models.UserTypes.email] = None, phone_number: typing.Optional[models.UserTypes.phone_number] = None):

    code = models.OTP.generate_code()
    otp = await models.OTP.api_post(models.OTP.PostParams.model_construct(
        session=session, c=c, authorized_user_id=user._id, create_model=models.OTPAdminCreate(
            user_id=user._id, hashed_code=models.OTP.hash_code(code), lifespan=c.auth['credential_lifespans']['otp'])
    ))

    if email:
        c.send_email(email, 'OTP', 'Your OTP is: {}'.format(code))
    if phone_number:
        c.send_sms(phone_number, 'Your OTP is: {}'.format(code))


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
    tokenUrl="auth/token/")


class DetailOnlyResponse(BaseModel):
    detail: str


class NotFoundResponse(DetailOnlyResponse):
    pass


class MakeGetAuthorizationDependencyKwargs(typing.TypedDict, total=False):
    required_scopes: typing.Optional[set[types.Scope.name]]
    permitted_auth_credential_types: typing.Optional[set[types.AuthCredential.type]]
    override_lifetime: typing.Optional[datetime.timedelta]


class GetAuthorizationReturn(BaseModel):
    isAuthorized: bool = False
    exception: typing.Optional[exceptions.StatusCodeAndDetail] = None
    user: typing.Optional[user_model_module.UserPrivate] = None
    scope_ids: typing.Optional[set[types.Scope.id]] = None
    auth_credential: typing.Optional[models.AuthCredentialClass] = None

    @property
    def _user_id(self):
        if self.auth_credential:
            if issubclass(self.auth_credential, auth_credential.Table):
                if self.auth_credential.user:
                    return self.auth_credential.user.id
        return None


class GetAuthorizationFromTokenReturn(GetAuthorizationReturn):
    auth_credential: typing.Optional[models.AuthCredentialTokenClass] = None


async def get_auth_from_auth_credential_table_inst(
        session: AsyncSession,
        auth_credential_table_inst: models.AuthCredentialTableClass,
        required_scopes: set[types.Scope.name] = set(),
        override_lifetime: typing.Optional[datetime.timedelta] = None,
        dt_now=datetime.datetime.now(datetime.UTC),
) -> GetAuthorizationReturn:

    if not auth_credential_table_inst:
        return GetAuthorizationReturn(exception=exceptions.authorization_expired())

    # if it expired, delete it
    if dt_now > auth_credential_table_inst.expiry:
        await session.delete(auth_credential_table_inst)
        await session.commit()
        return GetAuthorizationReturn(exception=exceptions.authorization_expired())

    if override_lifetime != None:
        if dt_now > (auth_credential_table_inst.issued + override_lifetime):
            await session.delete(auth_credential_table_inst)
            await session.commit()
            return GetAuthorizationReturn(exception=exceptions.authorization_expired())

    user = auth_credential_table_inst.user
    if user == None:
        return GetAuthorizationReturn(exception=exceptions.user_not_found())

    scope_ids = set(await auth_credential_table_inst.get_scope_ids(session))

    required_scope_ids = set(
        [settings.SCOPE_NAME_MAPPING[scope_name]
            for scope_name in required_scopes]
    )
    if not required_scope_ids.issubset(scope_ids):
        return GetAuthorizationReturn(exception=exceptions.not_permitted())

    return GetAuthorizationReturn(
        isAuthorized=True,
        user=user_model_module.UserPrivate.model_validate(user),
        scope_ids=scope_ids,
        auth_credential=auth_credential_table_inst
    )


async def get_auth_from_token(
        token: typing.Optional[types.JwtEncodedStr] = None,
        required_scopes: set[types.Scope.name] = set(),
        permitted_auth_credential_types: set[models.AuthCredentialTokenType] = set(
            c.auth_type for c in models.AUTH_CREDENTIAL_TOKEN_CLASSES),
        override_lifetime: typing.Optional[datetime.timedelta] = None
) -> GetAuthorizationReturn:

    if token == None:
        return GetAuthorizationReturn(exception=exceptions.missing_authorization())

    # make sure the token is a valid jwt
    try:
        payload: dict = c.jwt_decode(token)
    except:
        return GetAuthorizationReturn(exception=exceptions.improper_format())

    # make sure "type" is in the jwt
    if models.AuthCredential.JwtIO._TYPE_CLAIM not in payload:
        return GetAuthorizationReturn(exception=exceptions.missing_required_claims())

    # make sure the "type" is a permitted auth_credential type
    auth_type: models.AuthCredentialTypes.type = payload['type']
    if auth_type not in permitted_auth_credential_types:
        return GetAuthorizationReturn(exception=exceptions.authorization_type_not_permitted())

    AuthCredentialClass = models.AUTH_CREDENTIAL_TYPE_TO_CLASS[auth_type]

    # validate the jwt claims
    if not AuthCredentialClass.validate_jwt_claims(payload):
        return GetAuthorizationReturn(exception=exceptions.missing_required_claims())

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
        return GetAuthorizationReturn(exception=exceptions.authorization_expired())
    if override_lifetime != None:
        if dt_now > auth_credential_from_jwt.issued + override_lifetime:
            return GetAuthorizationReturn(exception=exceptions.authorization_expired())

    # if the auth_credentail is a table, it will need to be in the db
    # for example, SignUp is a JWT only credential, so it will not be in the db
    if issubclass(AuthCredentialClass, models.Table):
        async with c.AsyncSession() as session:
            auth_credential_from_db = await AuthCredentialClass.read(
                session, auth_credential_from_jwt._id)

            response = await get_auth_from_auth_credential_table_inst(
                session, auth_credential_from_db, required_scopes, override_lifetime, dt_now)
            return response
    else:
        # non-table auth_credentials have no scopes
        if required_scopes:
            return GetAuthorizationReturn(exception=exceptions.not_permitted())

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

                raise exceptions.Base(
                    get_authorization_return.exception, logout=logout_on_exception
                )

        return get_authorization_return
    return get_authorization_dependency


class AuthCredentialIdTypeAndExpiry(BaseModel):
    id: models.AuthCredentialId | None
    type: models.AuthCredentialTypes.type
    expiry: models.AuthCredentialTypes.expiry


class GetAuthBaseReturn(BaseModel):
    user: typing.Optional[user_model_module.UserPrivate]
    scope_ids: typing.Optional[set[types.Scope.id]]
    auth_credential: typing.Optional[AuthCredentialIdTypeAndExpiry]


assert settings.SHARED_CONSTANTS['auth_key'] == 'auth'


class GetAuthReturn(BaseModel):
    auth: GetAuthBaseReturn


def get_auth(get_authorization_return: GetAuthorizationReturn) -> GetAuthReturn:

    return GetAuthReturn(auth=GetAuthBaseReturn(
        user=get_authorization_return.user,
        scope_ids=get_authorization_return.scope_ids,
        auth_credential=None if not get_authorization_return.auth_credential else
        AuthCredentialIdTypeAndExpiry(
            id=get_authorization_return.auth_credential.id,
            type=get_authorization_return.auth_credential.auth_type,
            expiry=get_authorization_return.auth_credential.expiry
        )
    ))
