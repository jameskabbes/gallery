import React, { Component } from 'react';
import { paths, operations, components } from '../../openapi_schema';
import { ExtractResponseTypes } from '../../types';
import { callApi } from '../../utils/Api';
import { toast } from 'react-toastify';
import { toastTemplate } from '../Toast';
import { AuthReducerAction } from '../../types';

const API_ENDPOINT = '/login/';
const API_METHOD = 'post';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function logInUserFunc(
  formData: paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/x-www-form-urlencoded'],
  authContextDispatch: React.Dispatch<AuthReducerAction>
): Promise<ResponseTypesByStatus['200'] | null> {
  let toastId = toast.loading('Logging in');

  async function setToken(data: ResponseTypesByStatus['200']) {
    authContextDispatch({ type: 'SET_TOKEN', payload: data.token });
  }
  async function login(data: ResponseTypesByStatus['200']) {
    authContextDispatch({ type: 'LOGIN', payload: data.auth });
  }

  const { data, response } = await callApi<
    ResponseTypesByStatus[keyof ResponseTypesByStatus],
    paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/x-www-form-urlencoded']
  >({
    endpoint: API_ENDPOINT,
    method: API_METHOD,
    body: new URLSearchParams(formData).toString(),
    overwriteHeaders: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });

  if (response.status === 200) {
    const apiData = data as ResponseTypesByStatus['200'];

    console.log(apiData);

    await setToken(apiData);
    await login(apiData);

    toast.update(toastId, {
      ...toastTemplate,
      render: `Welcome ${apiData.auth.user.username}`,
      type: 'success',
    });
    return apiData;
  } else {
    console.error('Error logging in:', response.status, data);
    toast.update(toastId, {
      ...toastTemplate,
      render: `Could not log in`,
      type: 'error',
    });
    return null;
  }
}

export { logInUserFunc };
