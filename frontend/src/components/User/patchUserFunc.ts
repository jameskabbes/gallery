import React, { Component } from 'react';
import { paths, operations, components } from '../../openapi_schema';
import { ExtractResponseTypes } from '../../types';
import { callApi } from '../../utils/Api';
import { AuthReducerAction } from '../../types';
import { CallApiReturn } from '../../types';
import { toast } from 'react-toastify';
import { toastTemplate } from '../Toast';

const API_ENDPOINT = '/users/{user_id}/';
const API_METHOD = 'patch';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function patchUserFunc(
  userId: components['schemas']['UserPublic']['id'],
  formData: paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json'],
  authContextDispatch: React.Dispatch<AuthReducerAction>
): Promise<CallApiReturn<ResponseTypesByStatus[keyof ResponseTypesByStatus]>> {
  let toastId = toast.loading('Updating user');

  const { data, response } = await callApi<
    ResponseTypesByStatus[keyof ResponseTypesByStatus],
    paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
  >({
    endpoint: API_ENDPOINT.replace('{user_id}', userId),
    method: API_METHOD,
    data: formData,
  });

  if (response.status === 200) {
    const apiData = data as ResponseTypesByStatus['200'];
    authContextDispatch({ type: 'SET_AUTH_USER', payload: apiData });
    toast.update(toastId, {
      ...toastTemplate,
      render: `Updated user`,
      type: 'success',
    });
  } else if (
    response.status === 401 ||
    response.status === 403 ||
    response.status === 404 ||
    response.status === 409
  ) {
    const apiData = data as ResponseTypesByStatus[
      | '401'
      | '403'
      | '404'
      | '409'];

    if (response.status === 401 || response.status === 404) {
      authContextDispatch({ type: 'LOGOUT' });
    }

    toast.update(toastId, {
      ...toastTemplate,
      render: apiData.detail,
      type: 'error',
    });
  } else {
    toast.update(toastId, {
      ...toastTemplate,
      render: `Could not update user`,
      type: 'error',
    });
  }

  return { data, response };
}

export { patchUserFunc };
