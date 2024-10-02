import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/Api';
import { paths, operations, components } from '../../openapi_schema';
import { CallApiReturn, ExtractResponseTypes, ToastContext } from '../../types';

const API_ENDPOINT = '/api-keys/';
const API_METHOD = 'post';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function postAPIKey(
  apiKeyCreate: paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json'],
  toastContext: ToastContext
): Promise<CallApiReturn<ResponseTypesByStatus[keyof ResponseTypesByStatus]>> {
  let toastId = toastContext.makePending({
    message: 'Making API Key...',
  });

  const { data, response } = await callApi<
    ResponseTypesByStatus[keyof ResponseTypesByStatus],
    paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
  >({
    endpoint: API_ENDPOINT,
    method: API_METHOD,
    data: apiKeyCreate,
  });

  if (response.status === 200) {
    const apiData = data as ResponseTypesByStatus['200'];
    toastContext.update(toastId, {
      message: `Created API Key`,
      type: 'success',
    });
  } else {
    toastContext.update(toastId, {
      message: `Could not create API Key`,
      type: 'error',
    });
  }
  return { data, response };
}

export { postAPIKey };
