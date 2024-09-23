import React, { Component } from 'react';
import { paths, operations, components } from '../../openapi_schema';
import { ExtractResponseTypes } from '../../types';
import { callApi } from '../../utils/Api';
import { CallApiReturn, ToastContext, AuthContext } from '../../types';

const API_ENDPOINT = '/users/{user_id}/';
const API_METHOD = 'patch';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function patchUserFunc(
  userId: components['schemas']['UserPublic']['id'],
  formData: paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json'],
  authContext: AuthContext,
  toastContext: ToastContext
): Promise<CallApiReturn<ResponseTypesByStatus[keyof ResponseTypesByStatus]>> {
  let toastId = toastContext.makePending({
    message: 'Updating user...',
  });
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
    toastContext.update(toastId, {
      message: `Updated user`,
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

    toastContext.update(toastId, {
      message: apiData.detail,
      type: 'error',
    });
  } else {
    toastContext.update(toastId, {
      message: 'Could not update user',
      type: 'error',
    });
  }

  return { data, response };
}

export { patchUserFunc };
