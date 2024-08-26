import React, { Component } from 'react';
import { paths, operations, components } from '../../openapi_schema';
import { ExtractResponseTypes } from '../../types';
import { callBackendApi } from '../../utils/Api';
import { toast } from 'react-toastify';
import { toastTemplate } from '../Toast';
import { AuthReducerAction } from '../../types';

const API_ENDPOINT = '/users/{user_id}/';
const API_METHOD = 'patch';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function patchUserFunc(
  userId: components['schemas']['UserPublic']['id'],
  formData: paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json'],
  authContextDispatch: React.Dispatch<AuthReducerAction>
): Promise<ResponseTypesByStatus['200'] | null> {
  let toastId = toast.loading('Updating user');

  console.log('calling api');

  const { data, response } = await callBackendApi<
    ResponseTypesByStatus[keyof ResponseTypesByStatus],
    paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
  >({
    endpoint: API_ENDPOINT.replace('{user_id}', userId),
    method: API_METHOD,
    data: formData,
  });
  console.log('api called');
  console.log(data);
  console.log(response);

  if (response.status === 200) {
    const apiData = data as ResponseTypesByStatus['200'];
    toast.update(toastId, {
      ...toastTemplate,
      render: `Updated user`,
      type: 'success',
    });
    authContextDispatch({ type: 'SET_AUTH_USER', payload: apiData });
  } else {
    toast.update(toastId, {
      ...toastTemplate,
      render: `Could not update user`,
      type: 'error',
    });
    return null;
  }
}

export { patchUserFunc };
