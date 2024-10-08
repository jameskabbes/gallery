import React, { useContext } from 'react';
import { useGoogleLogin } from '@react-oauth/google';
import { callApi } from '../../utils/Api';
import { ExtractResponseTypes } from '../../types';
import { paths, operations, components } from '../../openapi_schema';
import { AuthContext } from '../../contexts/Auth';
import { LogInContext } from '../../contexts/LogIn';
import { AuthModalsContext } from '../../contexts/AuthModals';

const API_ENDPOINT = '/auth/login/google/';
const API_METHOD = 'post';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

type TRequestData =
  paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json'];

function useLogInWithGoogle() {
  const authContext = useContext(AuthContext);
  const authModalsContext = useContext(AuthModalsContext);
  const logInContext = useContext(LogInContext);

  async function call(request_data: TRequestData) {
    const { data, response } = await callApi<
      ResponseTypesByStatus[keyof ResponseTypesByStatus],
      TRequestData
    >({
      endpoint: API_ENDPOINT,
      method: API_METHOD,
      data: request_data,
    });

    if (response.status == 200) {
      const apiData = data as ResponseTypesByStatus['200'];
      authContext.updateFromApiResponse(apiData);
      authModalsContext.setActiveModalType(null);
    }
  }

  const googleLogin = useGoogleLogin({
    onSuccess: (res) => {
      console.log(res);
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
