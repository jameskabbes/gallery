import React, { useContext } from 'react';
import { useGoogleLogin } from '@react-oauth/google';
import { callApi } from '../../utils/Api';
import { ExtractResponseTypes } from '../../types';
import { paths, operations, components } from '../../openapi_schema';
import { AuthContext } from '../../contexts/Auth';

const API_ENDPOINT = '/auth/google/';
const API_METHOD = 'post';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

type TRequestData =
  paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json'];

function useLogInWithGoogle() {
  const authContext = useContext(AuthContext);

  async function call(request_data: TRequestData) {
    const { data: apiData, response } = await callApi<
      ResponseTypesByStatus[keyof ResponseTypesByStatus],
      TRequestData
    >({
      endpoint: '/auth/google/',
      method: 'post',
      data: request_data,
    });

    if (response.status == 200) {
      const data = apiData as ResponseTypesByStatus['200'];
      authContext.dispatch({ type: 'UPDATE_FROM_API_RESPONSE', payload: data });
    }
  }

  const googleLogin = useGoogleLogin({
    onSuccess: (res) => {
      call({
        access_token: res.access_token,
      });
    },
  });

  function logInWithGoogle() {
    googleLogin();
  }

  return { logInWithGoogle };
}

export { useLogInWithGoogle };
