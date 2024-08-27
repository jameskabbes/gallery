import React, { Component } from 'react';
import { paths, operations, components } from '../../openapi_schema';
import { ExtractResponseTypes } from '../../types';
import { callApi } from '../../utils/Api';
import { toast } from 'react-toastify';
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
    return apiData;
  } else {
    return null;
  }
}

export { patchUserFunc };
