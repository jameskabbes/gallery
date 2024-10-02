import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/Api';
import { paths, operations, components } from '../../openapi_schema';
import { CallApiReturn, ExtractResponseTypes, ToastContext } from '../../types';

const API_ENDPOINT = '/user-access-tokens/{user_access_token_id}/';
const API_METHOD = 'delete';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function deleteUserAccessToken(
  user_access_token_id: paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['path']['user_access_token_id'],
  toastContext: ToastContext
): Promise<CallApiReturn<ResponseTypesByStatus[keyof ResponseTypesByStatus]>> {
  let toastId = toastContext.makePending({
    message: 'Deleting user access token...',
  });

  const { data, response } = await callApi<
    ResponseTypesByStatus[keyof ResponseTypesByStatus]
  >({
    endpoint: API_ENDPOINT.replace(
      '{user_access_token_id}',
      user_access_token_id
    ),
    method: API_METHOD,
  });

  if (response.status === 204) {
    const apiData = data as ResponseTypesByStatus['204'];
    toastContext.update(toastId, {
      message: `Deleted user access token`,
      type: 'success',
    });
  } else {
    toastContext.update(toastId, {
      message: 'Could not delete user access token',
      type: 'error',
    });
  }
  return { data, response };
}

export { deleteUserAccessToken };
