import { paths } from '../openapi_schema';
import { createApiService, ResponseDataTypeByStatusCode } from '../utils/api';

// Auth
export const getAuth = createApiService('/auth/', 'get');
export const postLogInPassword = createApiService(
  '/auth/login/password/',
  'post'
);
export const postLogInGoogle = createApiService('/auth/login/google/', 'post');

export const postLogInMagicLink = createApiService(
  '/auth/login/magic-link/',
  'post'
);

export const postLogInOTPEmail = createApiService(
  '/auth/login/otp/email/',
  'post'
);

export const postLogInOTPPhoneNumber = createApiService(
  '/auth/login/otp/phone_number/',
  'post'
);

export const postSignUp = createApiService('/auth/signup/', 'post');

export const postLogOut = createApiService('/auth/logout/', 'post');

export const postRequestMagicLinkEmail = createApiService(
  '/auth/request/magic-link/email/',
  'post'
);

export const postRequestMagicLinkSMS = createApiService(
  '/auth/request/magic-link/sms/',
  'post'
);

export const postRequestOTPEmail = createApiService(
  '/auth/request/otp/email/',
  'post'
);

export const postRequestOTPSMS = createApiService(
  '/auth/request/otp/sms/',
  'post'
);

export const postRequestSignUp = createApiService(
  '/auth/request/signup/',
  'post'
);

// User

export const patchMe = createApiService('/users/me/', 'patch');

export const getMe = createApiService('/users/me/', 'get');

export const deleteMe = createApiService('/users/me/', 'delete');

export const getIsUserUsernameAvailable = createApiService(
  '/users/available/username/{username}/',
  'get'
);

// User Access Tokens

export const getUserAccessTokens = createApiService(
  '/user-access-tokens/',
  'get'
);

export const deleteUserAccessToken = createApiService(
  '/user-access-tokens/{user_access_token_id}/',
  'delete'
);

// Api Keys
export const getApiKey = createApiService('/api-keys/{api_key_id}/', 'get');

export const getApiKeys = createApiService('/api-keys/', 'get');

export const postApiKey = createApiService('/api-keys/', 'post');

export const patchApiKey = createApiService('/api-keys/{api_key_id}/', 'patch');

export const deleteApiKey = createApiService(
  '/api-keys/{api_key_id}/',
  'delete'
);

export const getIsApiKeyAvailable = createApiService(
  '/api-keys/details/available/',
  'get'
);

export const getApiKeyJwt = createApiService(
  '/api-keys/{api_key_id}/generate-jwt/',
  'get'
);

// Api Key Scope
export const postApiKeyScope = createApiService(
  '/api-key-scopes/api-keys/{api_key_id}/scopes/{scope_id}/',
  'post'
);

export const deleteApiKeyScope = createApiService(
  '/api-key-scopes/api-keys/{api_key_id}/scopes/{scope_id}/',
  'delete'
);

// Gallery
export const postGallery = createApiService<'/galleries/', 'post'>(
  '/galleries/',
  'post'
);

export const patchGallery = createApiService(
  '/galleries/{gallery_id}/',
  'patch'
);

export const deleteGallery = createApiService(
  '/galleries/{gallery_id}/',
  'delete'
);

export const getIsGalleryAvailable = createApiService(
  '/galleries/details/available/',
  'get'
);

export const postGallerySync = createApiService(
  '/galleries/{gallery_id}/sync/',
  'post'
);

export const postGalleryFile = createApiService(
  '/galleries/{gallery_id}/upload/',
  'post'
);

// pages

export const getHomePage = createApiService('/pages/home/', 'get');

export const getStylesPage = createApiService('/pages/styles/', 'get');

export const getSettingsPage = createApiService('/pages/settings/', 'get');

export const getApiKeysSettingsPage = createApiService(
  '/pages/settings/api-keys/',
  'get'
);

export const getUserAccessTokensSettingsPage = createApiService(
  '/pages/settings/user-access-tokens/',
  'get'
);

export const getGalleryPage = createApiService(
  '/pages/galleries/{gallery_id}/',
  'get'
);
