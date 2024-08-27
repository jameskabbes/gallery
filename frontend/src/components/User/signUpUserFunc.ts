import React, { Component } from 'react';
import { paths, operations, components } from '../../openapi_schema';
import { ExtractResponseTypes } from '../../types';
import { callApi } from '../../utils/Api';
import { toast } from 'react-toastify';
import { toastTemplate } from '../Toast';
import { AuthReducerAction } from '../../types';

const API_ENDPOINT = '/signup/';
const API_METHOD = 'post';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function signUpUserFunc(
  userCreate: components['schemas']['UserCreate'],
  authContextDispatch: React.Dispatch<AuthReducerAction>
): Promise<ResponseTypesByStatus['200'] | null> {
  let toastId = toast.loading('Creating user');

  async function setToken(data: ResponseTypesByStatus['200']) {
    authContextDispatch({ type: 'SET_TOKEN', payload: data.token });
  }
  async function login(data: ResponseTypesByStatus['200']) {
    authContextDispatch({ type: 'LOGIN', payload: data.auth });
  }

  const { data, response } = await callApi<
    ResponseTypesByStatus[keyof ResponseTypesByStatus],
    components['schemas']['UserCreate']
  >({
    endpoint: API_ENDPOINT,
    method: API_METHOD,
    data: userCreate,
  });

  if (response.status === 200) {
    const apiData = data as ResponseTypesByStatus['200'];

    await setToken(apiData);
    await login(apiData);

    toast.update(toastId, {
      ...toastTemplate,
      render: 'Created new user: ' + apiData.auth.user.username,
      type: 'success',
    });

    return apiData;
  } else {
    console.error('Error creating user:', response.status, data);
    toast.update(toastId, {
      ...toastTemplate,
      render: 'Could not create user',
      type: 'error',
    });
    return null;
  }
}

export { signUpUserFunc };
