import React, { Component } from 'react';
import { paths, operations, components } from '../../openapi_schema';
import { ExtractResponseTypes } from '../../types';
import { callBackendApi } from '../../utils/Api';
import { toast } from 'react-toastify';
import { toastTemplate } from '../Toast';

const API_ENDPOINT = '/users/';
const API_METHOD = 'post';

type AllResponseTypes = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function createUserFunc(
  userCreate: components['schemas']['UserCreate']
): Promise<AllResponseTypes['200'] | null> {
  let userPublic: components['schemas']['UserPublic'] = {
    id: '__loading__',
    username: userCreate.username,
  };

  let toastId = toast.loading('Creating user');

  // wait for 2 seconds
  await new Promise((resolve) => setTimeout(resolve, 2000));

  const { data, response } = await callBackendApi<
    AllResponseTypes[keyof AllResponseTypes],
    components['schemas']['UserCreate']
  >({
    endpoint: API_ENDPOINT,
    method: API_METHOD,
    data: userCreate,
  });

  if (response.status === 200) {
    const apiData = data as AllResponseTypes['200'];
    toast.update(toastId, {
      ...toastTemplate,
      render: 'User created',
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

export { createUserFunc };
