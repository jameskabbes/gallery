import React, { Component } from 'react';
import { paths, operations, components } from '../../openapi_schema';
import { CallApiReturn, ExtractResponseTypes, ToastContext } from '../../types';
import { callApi } from '../../utils/Api';
import { AuthReducerAction } from '../../types';

const API_ENDPOINT = '/login/';
const API_METHOD = 'post';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function logInUserFunc(
  formData: paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/x-www-form-urlencoded'],
  authContextDispatch: React.Dispatch<AuthReducerAction>,
  toastContext: ToastContext
): Promise<CallApiReturn<ResponseTypesByStatus[keyof ResponseTypesByStatus]>> {
  let toastId = toastContext.makePending({
    message: 'Logging in...',
  });

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

  if (response.status == 200) {
    const apiData = data as ResponseTypesByStatus['200'];

    await setToken(apiData);
    await login(apiData);

    toastContext.update(toastId, {
      message: `Welcome ${apiData.auth.user.username}`,
      type: 'success',
    });
  } else if (response.status == 401) {
    const apiData = data as ResponseTypesByStatus['401'];
    toastContext.update(toastId, {
      message: apiData.detail,
      type: 'error',
    });
  } else {
    toastContext.update(toastId, {
      message: 'Could not log in',
      type: 'error',
    });
  }
  return { data, response };
}

export { logInUserFunc };
