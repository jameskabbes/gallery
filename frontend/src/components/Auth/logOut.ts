import React, { Component } from 'react';
import { paths, operations, components } from '../../openapi_schema';
import { callApi } from '../../utils/Api';
import {
  ExtractResponseTypes,
  CallApiReturn,
  AuthContext,
  ToastContext,
} from '../../types';
import { useConfirmationModal } from '../../utils/useConfirmationModal';

const API_ENDPOINT = '/auth/logout/';
const API_METHOD = 'post';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function logOut(
  authContext: AuthContext,
  toastContext: ToastContext
): Promise<CallApiReturn<ResponseTypesByStatus[keyof ResponseTypesByStatus]>> {
  let toastId = toastContext.makePending({
    message: 'Logging out...',
  });
  const { data, response } = await callApi<
    ResponseTypesByStatus[keyof ResponseTypesByStatus]
  >({
    endpoint: API_ENDPOINT,
    method: API_METHOD,
    authContext,
  });

  if (response.status === 200) {
    const apiData = data as ResponseTypesByStatus['200'];
    authContext.logOut(toastId);
  } else {
    toastContext.update(toastId, {
      message: 'Error logging out',
      type: 'error',
    });
  }

  return { data, response };
}

export { logOut };
