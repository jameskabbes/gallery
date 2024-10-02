import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/Api';
import { paths, operations, components } from '../../openapi_schema';
import { CallApiReturn, ExtractResponseTypes, ToastContext } from '../../types';

const API_ENDPOINT = '/api-keys/{api_key_id}/';
const API_METHOD = 'delete';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function deleteAPIKey(
  api_key_id: paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['path']['api_key_id'],
  toastContext: ToastContext
): Promise<CallApiReturn<ResponseTypesByStatus[keyof ResponseTypesByStatus]>> {
  let toastId = toastContext.makePending({
    message: 'Deleting API Key...',
  });

  const { data, response } = await callApi<
    ResponseTypesByStatus[keyof ResponseTypesByStatus]
  >({
    endpoint: API_ENDPOINT.replace('{api_key_id}', api_key_id),
    method: API_METHOD,
  });

  if (response.status === 204) {
    const apiData = data as ResponseTypesByStatus['204'];
    toastContext.update(toastId, {
      message: `Deleted API Key`,
      type: 'success',
    });
  } else {
    toastContext.update(toastId, {
      message: 'Could not delete API Key',
      type: 'error',
    });
  }
  return { data, response };
}

export { deleteAPIKey };
