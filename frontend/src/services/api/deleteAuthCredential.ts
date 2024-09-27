import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/Api';
import { paths, operations, components } from '../../openapi_schema';
import { CallApiReturn, ExtractResponseTypes, ToastContext } from '../../types';

const API_ENDPOINT = '/auth-credentials/{auth_credential_id}/';
const API_METHOD = 'delete';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function deleteAuthCredential(
  auth_credential_id: paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['path']['auth_credential_id'],
  toastContext: ToastContext
): Promise<CallApiReturn<ResponseTypesByStatus[keyof ResponseTypesByStatus]>> {
  let toastId = toastContext.makePending({
    message: 'Deleting authorization credential...',
  });

  const { data, response } = await callApi<
    ResponseTypesByStatus[keyof ResponseTypesByStatus],
    paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['path']['auth_credential_id']
  >({
    endpoint: API_ENDPOINT.replace('{auth_credential_id}', auth_credential_id),
    method: API_METHOD,
  });

  if (response.status === 204) {
    const apiData = data as ResponseTypesByStatus['204'];
    toastContext.update(toastId, {
      message: `Deleted authorization credential`,
      type: 'success',
    });
  } else {
    toastContext.update(toastId, {
      message: 'Could not delete authorization credential',
      type: 'error',
    });
  }
  return { data, response };
}

export { deleteAuthCredential };
