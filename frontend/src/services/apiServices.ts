import { createApiService, ExtractResponseTypes } from '../utils/api';
import { paths, operations, components } from '../openapi_schema';

// Auth
const getAuth = createApiService('/auth/', 'get');
type GetAuthResponses = ExtractResponseTypes<paths['/auth/']['get']>;

const postLogInPassword = createApiService('/auth/login/password/', 'post');
type PostLogInPasswordResponses = ExtractResponseTypes<
  paths['/auth/login/password/']['post']
>;

const postLogInGoogle = createApiService('/auth/login/google/', 'post');
type PostLogInGoogleResponses = ExtractResponseTypes<
  paths['/auth/login/google/']['post']
>;

const postLogInMagicLink = createApiService('/auth/login/magic-link/', 'post');
type PostLogInMagicLinkResponses = ExtractResponseTypes<
  paths['/auth/login/magic-link/']['post']
>;

const postLogInOTPEmail = createApiService('/auth/login/otp/email/', 'post');
type PostLogInOTPEmailResponses = ExtractResponseTypes<
  paths['/auth/login/otp/email/']['post']
>;

const postLogInOTPPhoneNumber = createApiService(
  '/auth/login/otp/phone_number/',
  'post'
);
type PostLogInOTPPhoneNumberResponses = ExtractResponseTypes<
  paths['/auth/login/otp/phone_number/']['post']
>;

const postSignUp = createApiService('/auth/signup/', 'post');
type PostSignUpResponses = ExtractResponseTypes<paths['/auth/signup/']['post']>;

const postLogOut = createApiService('/auth/logout/', 'post');
type PostLogOutResponses = ExtractResponseTypes<paths['/auth/logout/']['post']>;

const postRequestMagicLinkEmail = createApiService(
  '/auth/request/magic-link/email/',
  'post'
);
type PostRequestMagicLinkEmailResponses = ExtractResponseTypes<
  paths['/auth/request/magic-link/email/']['post']
>;

const postRequestMagicLinkSMS = createApiService(
  '/auth/request/magic-link/sms/',
  'post'
);
type PostRequestMagicLinkSMSResponses = ExtractResponseTypes<
  paths['/auth/request/magic-link/sms/']['post']
>;

const postRequestOTPEmail = createApiService(
  '/auth/request/otp/email/',
  'post'
);
type PostRequestOTPEmailResponses = ExtractResponseTypes<
  paths['/auth/request/otp/email/']['post']
>;

const postRequestOTPSMS = createApiService('/auth/request/otp/sms/', 'post');
type PostRequestOTPSMSResponses = ExtractResponseTypes<
  paths['/auth/request/otp/sms/']['post']
>;

const postRequestSignUpEmail = createApiService(
  '/auth/request/signup/email/',
  'post'
);
type PostRequestSignUpEmailResponses = ExtractResponseTypes<
  paths['/auth/request/signup/email/']['post']
>;

// User

const patchMe = createApiService('/users/me/', 'patch');
type PatchMeResponses = ExtractResponseTypes<paths['/users/me/']['patch']>;

const getMe = createApiService('/users/me/', 'get');
type GetMeResponses = ExtractResponseTypes<paths['/users/me/']['get']>;

const getIsUserUsernameAvailable = createApiService(
  '/users/available/username/{username}/',
  'get'
);
type GetIsUserUsernameAvailableResponses = ExtractResponseTypes<
  paths['/users/available/username/{username}/']['get']
>;

// User Access Tokens
const deleteUserAccessToken = createApiService(
  '/user-access-tokens/{user_access_token_id}/',
  'delete'
);
type DeleteUserAccessTokenResponses = ExtractResponseTypes<
  paths['/user-access-tokens/{user_access_token_id}/']['delete']
>;

// Api Keys
const getApiKey = createApiService('/api-keys/{api_key_id}/', 'get');
type GetApiKeyResponses = ExtractResponseTypes<
  paths['/api-keys/{api_key_id}/']['get']
>;

const getApiKeys = createApiService('/api-keys/', 'get');
type GetApiKeysResponses = ExtractResponseTypes<paths['/api-keys/']['get']>;

const postApiKey = createApiService('/api-keys/', 'post');
type PostApiKeyResponses = ExtractResponseTypes<paths['/api-keys/']['post']>;

const patchApiKey = createApiService('/api-keys/{api_key_id}/', 'patch');
type PatchApiKeyResponses = ExtractResponseTypes<
  paths['/api-keys/{api_key_id}/']['patch']
>;

const deleteApiKey = createApiService('/api-keys/{api_key_id}/', 'delete');
type DeleteApiKeyResponses = ExtractResponseTypes<
  paths['/api-keys/{api_key_id}/']['delete']
>;

const getIsApiKeyAvailable = createApiService(
  '/api-keys/details/available/',
  'get'
);
type GetIsApiKeyAvailableResponses = ExtractResponseTypes<
  paths['/api-keys/details/available/']['get']
>;

const getApiKeyJwt = createApiService(
  '/api-keys/{api_key_id}/generate-jwt/',
  'get'
);
type GetApiKeyJwtResponses = ExtractResponseTypes<
  paths['/api-keys/{api_key_id}/generate-jwt/']['get']
>;

// Api Key Scope
const postApiKeyScope = createApiService(
  '/api-key-scopes/api-keys/{api_key_id}/scopes/{scope_id}/',
  'post'
);
type PostApiKeyScopeResponses = ExtractResponseTypes<
  paths['/api-key-scopes/api-keys/{api_key_id}/scopes/{scope_id}/']['post']
>;

const deleteApiKeyScope = createApiService(
  '/api-key-scopes/api-keys/{api_key_id}/scopes/{scope_id}/',
  'delete'
);
type DeleteApiKeyScopeResponses = ExtractResponseTypes<
  paths['/api-key-scopes/api-keys/{api_key_id}/scopes/{scope_id}/']['delete']
>;

// Gallery
const postGallery = createApiService('/galleries/', 'post');
type PostGalleryResponses = ExtractResponseTypes<paths['/galleries/']['post']>;

const patchGallery = createApiService('/galleries/{gallery_id}/', 'patch');
type PatchGalleryResponses = ExtractResponseTypes<
  paths['/galleries/{gallery_id}/']['patch']
>;

const deleteGallery = createApiService('/galleries/{gallery_id}/', 'delete');
type DeleteGalleryResponses = ExtractResponseTypes<
  paths['/galleries/{gallery_id}/']['delete']
>;

const getIsGalleryAvailable = createApiService(
  '/galleries/details/available/',
  'get'
);
type GetIsGalleryAvailableResponses = ExtractResponseTypes<
  paths['/galleries/details/available/']['get']
>;

const postGallerySync = createApiService(
  '/galleries/{gallery_id}/sync/',
  'post'
);
type PostGallerySyncResponses = ExtractResponseTypes<
  paths['/galleries/{gallery_id}/sync/']['post']
>;

const postGalleryFile = createApiService(
  '/galleries/{gallery_id}/upload/',
  'post'
);
type PostGalleryFileResponses = ExtractResponseTypes<
  paths['/galleries/{gallery_id}/upload/']['post']
>;

// pages

const getHomePage = createApiService('/pages/home/', 'get');
type GetHomePageResponses = ExtractResponseTypes<paths['/pages/home/']['get']>;

const getStylesPage = createApiService('/pages/styles/', 'get');
type GetStylesPageResponses = ExtractResponseTypes<
  paths['/pages/styles/']['get']
>;

const getSettingsPage = createApiService('/pages/settings/', 'get');
type GetSettingsPageResponses = ExtractResponseTypes<
  paths['/pages/settings/']['get']
>;

const getGalleryPage = createApiService(
  '/pages/galleries/{gallery_id}/',
  'get'
);
type GetGalleryPageResponses = ExtractResponseTypes<
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
  getGalleryPage,
  GetGalleryPageResponses,
  getHomePage,
  GetHomePageResponses,
};
