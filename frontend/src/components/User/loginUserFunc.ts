import React, { Component } from 'react';
import { paths, operations, components } from '../../openapi_schema';
import { ExtractResponseTypes } from '../../types';
import { callBackendApi } from '../../utils/Api';
import { toast } from 'react-toastify';
import { toastTemplate } from '../Toast';

import siteConfig from '../../../siteConfig.json';

const API_ENDPOINT = '/token/';
const API_METHOD = 'post';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function loginUserFunc(
  formData: paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/x-www-form-urlencoded']
): Promise<ResponseTypesByStatus['200'] | null> {
  // Simple validation

  let toastId = toast.loading('Logging in');

  const { data, response } = await callBackendApi<
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
    console.log(data);
    console.log(response);
    localStorage.setItem(siteConfig['access_token_key'], apiData.access_token);
    toast.update(toastId, {
      ...toastTemplate,
      render: 'Logged in',
      type: 'success',
    });
    return apiData;
  } else {
    console.error('Error logging in:', response.status, data);
    toast.update(toastId, {
      ...toastTemplate,
      render: 'Could not log in',
      type: 'error',
    });
    return null;
  }
}

export { loginUserFunc };
