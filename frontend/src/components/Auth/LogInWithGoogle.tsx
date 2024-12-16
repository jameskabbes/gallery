import React, { useContext } from 'react';
import { useGoogleLogin } from '@react-oauth/google';
import { ExtractResponseTypes } from '../../types';
import { paths, operations, components } from '../../openapi_schema';
import { AuthContext } from '../../contexts/Auth';
import { postLogInGoogle } from '../../services/api/postLogInGoogle';
import { GlobalModalsContext } from '../../contexts/GlobalModals';

const API_ENDPOINT = '/auth/login/google/';
const API_METHOD = 'post';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

type TRequestData =
  paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json'];

function useLogInWithGoogle() {
  const authContext = useContext(AuthContext);
  const globalModalsContext = useContext(GlobalModalsContext);

  async function call(request_data: TRequestData) {
    const { data, status } = await postLogInGoogle(authContext, request_data);
    if (status == 200) {
      const apiData = data as ResponseTypesByStatus['200'];
      authContext.updateFromApiResponse(apiData);
      globalModalsContext.clearModal();
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
