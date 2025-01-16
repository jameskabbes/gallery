import {
  createApiService,
  RequestContentType,
  ResponseDataType,
  RequestDataType,
  ResponseContentType,
  ResponseDataTypeByStatusCode,
  RequestParamsType,
  RequestPathParamsType,
  //   ExtractRequestContentType,
} from '../utils/api';
import { paths, operations, components } from '../openapi_schema';

// Auth
const getAuth = createApiService('/auth/', 'get');
type GetAuthResponses = ResponseDataTypeByStatusCode<paths['/auth/']['get']>;

const postLogInPassword = createApiService('/auth/login/password/', 'post');
type PostLogInPasswordResponses = ResponseDataTypeByStatusCode<
  paths['/auth/login/password/']['post']
>;

const postLogInGoogle = createApiService('/auth/login/google/', 'post');
type PostLogInGoogleResponses = ResponseDataTypeByStatusCode<
  paths['/auth/login/google/']['post']
>;

const postLogInMagicLink = createApiService('/auth/login/magic-link/', 'post');
type PostLogInMagicLinkResponses = ResponseDataTypeByStatusCode<
  paths['/auth/login/magic-link/']['post']
>;

const postLogInOTPEmail = createApiService('/auth/login/otp/email/', 'post');
type PostLogInOTPEmailResponses = ResponseDataTypeByStatusCode<
  paths['/auth/login/otp/email/']['post']
>;

const postLogInOTPPhoneNumber = createApiService(
  '/auth/login/otp/phone_number/',
  'post'
);
type PostLogInOTPPhoneNumberResponses = ResponseDataTypeByStatusCode<
  paths['/auth/login/otp/phone_number/']['post']
>;

const postSignUp = createApiService('/auth/signup/', 'post');
type PostSignUpResponses = ResponseDataTypeByStatusCode<
  paths['/auth/signup/']['post']
>;

const postLogOut = createApiService('/auth/logout/', 'post');
type PostLogOutResponses = ResponseDataTypeByStatusCode<
  paths['/auth/logout/']['post']
>;

const postRequestMagicLinkEmail = createApiService(
  '/auth/request/magic-link/email/',
  'post'
);
type PostRequestMagicLinkEmailResponses = ResponseDataTypeByStatusCode<
  paths['/auth/request/magic-link/email/']['post']
>;

const postRequestMagicLinkSMS = createApiService(
  '/auth/request/magic-link/sms/',
  'post'
);
type PostRequestMagicLinkSMSResponses = ResponseDataTypeByStatusCode<
  paths['/auth/request/magic-link/sms/']['post']
>;

const postRequestOTPEmail = createApiService(
  '/auth/request/otp/email/',
  'post'
);
type PostRequestOTPEmailResponses = ResponseDataTypeByStatusCode<
  paths['/auth/request/otp/email/']['post']
>;

const postRequestOTPSMS = createApiService('/auth/request/otp/sms/', 'post');
type PostRequestOTPSMSResponses = ResponseDataTypeByStatusCode<
  paths['/auth/request/otp/sms/']['post']
>;

const postRequestSignUpEmail = createApiService(
  '/auth/request/signup/email/',
  'post'
);
type PostRequestSignUpEmailResponses = ResponseDataTypeByStatusCode<
  paths['/auth/request/signup/email/']['post']
>;

// User

const patchMe = createApiService('/users/me/', 'patch');
type PatchMeResponses = ResponseDataTypeByStatusCode<
  paths['/users/me/']['patch']
>;

const getMe = createApiService('/users/me/', 'get');
type GetMeResponses = ResponseDataTypeByStatusCode<paths['/users/me/']['get']>;

const getIsUserUsernameAvailable = createApiService(
  '/users/available/username/{username}/',
  'get'
);
type GetIsUserUsernameAvailableResponses = ResponseDataTypeByStatusCode<
  paths['/users/available/username/{username}/']['get']
>;

// User Access Tokens
const deleteUserAccessToken = createApiService(
  '/user-access-tokens/{user_access_token_id}/',
  'delete'
);
type DeleteUserAccessTokenResponses = ResponseDataTypeByStatusCode<
  paths['/user-access-tokens/{user_access_token_id}/']['delete']
>;

// Api Keys
const getApiKey = createApiService('/api-keys/{api_key_id}/', 'get');
type GetApiKeyResponses = ResponseDataTypeByStatusCode<
  paths['/api-keys/{api_key_id}/']['get']
>;

const getApiKeys = createApiService('/api-keys/', 'get');
type GetApiKeysResponses = ResponseDataTypeByStatusCode<
  paths['/api-keys/']['get']
>;

const postApiKey = createApiService('/api-keys/', 'post');
type PostApiKeyResponses = ResponseDataTypeByStatusCode<
  paths['/api-keys/']['post']
>;

const patchApiKey = createApiService('/api-keys/{api_key_id}/', 'patch');
type PatchApiKeyResponses = ResponseDataTypeByStatusCode<
  paths['/api-keys/{api_key_id}/']['patch']
>;

const deleteApiKey = createApiService('/api-keys/{api_key_id}/', 'delete');
type DeleteApiKeyResponses = ResponseDataTypeByStatusCode<
  paths['/api-keys/{api_key_id}/']['delete']
>;

const getIsApiKeyAvailable = createApiService(
  '/api-keys/details/available/',
  'get'
);
type GetIsApiKeyAvailableResponses = ResponseDataTypeByStatusCode<
  paths['/api-keys/details/available/']['get']
>;

const getApiKeyJwt = createApiService(
  '/api-keys/{api_key_id}/generate-jwt/',
  'get'
);
type GetApiKeyJwtResponses = ResponseDataTypeByStatusCode<
  paths['/api-keys/{api_key_id}/generate-jwt/']['get']
>;

// Api Key Scope
const postApiKeyScope = createApiService(
  '/api-key-scopes/api-keys/{api_key_id}/scopes/{scope_id}/',
  'post'
);
type PostApiKeyScopeResponses = ResponseDataTypeByStatusCode<
  paths['/api-key-scopes/api-keys/{api_key_id}/scopes/{scope_id}/']['post']
>;

const deleteApiKeyScope = createApiService(
  '/api-key-scopes/api-keys/{api_key_id}/scopes/{scope_id}/',
  'delete'
);
type DeleteApiKeyScopeResponses = ResponseDataTypeByStatusCode<
  paths['/api-key-scopes/api-keys/{api_key_id}/scopes/{scope_id}/']['delete']
>;

// Gallery
const postGallery = createApiService<
  '/galleries/',
  'post',
  'test',
  'application/xml'
>('/galleries/', 'post', 'application/xml');
type PostGalleryResponses = ResponseDataTypeByStatusCode<
  paths['/galleries/']['post']
>;

type A = RequestContentType<paths['/galleries/']['post']>;
type B = ResponseContentType<paths['/galleries/']['post']>;
type C = ResponseDataTypeByStatusCode<
  paths['/galleries/']['post'],
  'application/json',
  200
>;
type D = ResponseDataType<paths['/galleries/']['post']>;
type E = RequestDataType<paths['/galleries/']['post']>;
type F = RequestParamsType<paths['/galleries/']['post']>;
type G = RequestPathParamsType<paths['/galleries/']['post']>;

// postGallery({
//   requestContentType: 'application/json',
// });

const patchGallery = createApiService('/galleries/{gallery_id}/', 'patch');
type PatchGalleryResponses = ResponseDataTypeByStatusCode<
  paths['/galleries/{gallery_id}/']['patch']
>;

const deleteGallery = createApiService('/galleries/{gallery_id}/', 'delete');
type DeleteGalleryResponses = ResponseDataTypeByStatusCode<
  paths['/galleries/{gallery_id}/']['delete']
>;

const getIsGalleryAvailable = createApiService(
  '/galleries/details/available/',
  'get'
);
type GetIsGalleryAvailableResponses = ResponseDataTypeByStatusCode<
  paths['/galleries/details/available/']['get']
>;

const postGallerySync = createApiService(
  '/galleries/{gallery_id}/sync/',
  'post'
);
type PostGallerySyncResponses = ResponseDataTypeByStatusCode<
  paths['/galleries/{gallery_id}/sync/']['post']
>;

const postGalleryFile = createApiService(
  '/galleries/{gallery_id}/upload/',
  'post'
);
type PostGalleryFileResponses = ResponseDataTypeByStatusCode<
  paths['/galleries/{gallery_id}/upload/']['post']
>;

// pages

const getHomePage = createApiService('/pages/home/', 'get');
type GetHomePageResponses = ResponseDataTypeByStatusCode<
  paths['/pages/home/']['get']
>;

const getStylesPage = createApiService('/pages/styles/', 'get');
type GetStylesPageResponses = ResponseDataTypeByStatusCode<
  paths['/pages/styles/']['get']
>;

const getSettingsPage = createApiService('/pages/settings/', 'get');
type GetSettingsPageResponses = ResponseDataTypeByStatusCode<
  paths['/pages/settings/']['get']
>;

const getApiKeysSettingPage = createApiService(
  '/pages/settings/api-keys/',
  'get'
);

type GetApiKeysSettingPageResponses = ResponseDataTypeByStatusCode<
  paths['/pages/settings/api-keys/']['get']
>;

const getGalleryPage = createApiService(
  '/pages/galleries/{gallery_id}/',
  'get'
);
type GetGalleryPageResponses = ResponseDataTypeByStatusCode<
  paths['/pages/galleries/{gallery_id}/']['get']
>;

export {
  getAuth,
  GetAuthResponses,
  postLogInPassword,
  PostLogInPasswordResponses,
  postLogInGoogle,
  PostLogInGoogleResponses,
  postLogInMagicLink,
  PostLogInMagicLinkResponses,
  postLogInOTPEmail,
  PostLogInOTPEmailResponses,
  postLogInOTPPhoneNumber,
  PostLogInOTPPhoneNumberResponses,
  postSignUp,
  PostSignUpResponses,
  postLogOut,
  PostLogOutResponses,
  postRequestMagicLinkEmail,
  PostRequestMagicLinkEmailResponses,
  postRequestMagicLinkSMS,
  PostRequestMagicLinkSMSResponses,
  postRequestOTPEmail,
  PostRequestOTPEmailResponses,
  postRequestOTPSMS,
  PostRequestOTPSMSResponses,
  postRequestSignUpEmail,
  PostRequestSignUpEmailResponses,
  patchMe,
  PatchMeResponses,
  getMe,
  GetMeResponses,
  getIsUserUsernameAvailable,
  GetIsUserUsernameAvailableResponses,
  deleteUserAccessToken,
  DeleteUserAccessTokenResponses,
  getApiKey,
  GetApiKeyResponses,
  getApiKeys,
  GetApiKeysResponses,
  postApiKey,
  PostApiKeyResponses,
  patchApiKey,
  PatchApiKeyResponses,
  deleteApiKey,
  DeleteApiKeyResponses,
  getIsApiKeyAvailable,
  GetIsApiKeyAvailableResponses,
  getApiKeyJwt,
  GetApiKeyJwtResponses,
  postApiKeyScope,
  PostApiKeyScopeResponses,
  deleteApiKeyScope,
  DeleteApiKeyScopeResponses,
  postGallery,
  PostGalleryResponses,
  patchGallery,
  PatchGalleryResponses,
  deleteGallery,
  DeleteGalleryResponses,
  getIsGalleryAvailable,
  GetIsGalleryAvailableResponses,
  postGallerySync,
  PostGallerySyncResponses,
  postGalleryFile,
  PostGalleryFileResponses,
  getStylesPage,
  GetStylesPageResponses,
  getSettingsPage,
  GetSettingsPageResponses,
  getApiKeysSettingPage,
  GetApiKeysSettingPageResponses,
  getGalleryPage,
  GetGalleryPageResponses,
  getHomePage,
  GetHomePageResponses,
};
