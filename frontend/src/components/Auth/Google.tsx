import React from 'react';
import { GoogleLogin, CredentialResponse } from '@react-oauth/google';
import { callBackendApi } from '../../utils/Api';

async function onSuccess(credentialResponse: CredentialResponse) {
  console.log(credentialResponse);

  interface GoogleAuthResponse {
    user: string;
  }
  interface GoogleAuthRequest {
    token: CredentialResponse['credential'];
  }

  async function authGoogle() {
    return callBackendApi<GoogleAuthResponse, GoogleAuthRequest>({
      endpoint: '/auth/google/',
      method: 'POST',
      data: {
        token: credentialResponse.credential,
      },
    });
  }
  let a = await authGoogle();
  console.log(a);
}

export { onSuccess };
