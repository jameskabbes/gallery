import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/Api';
import { paths, operations, components } from '../../openapi_schema';
import {
  AuthContext,
  CallApiReturn,
  ExtractResponseTypes,
  ToastContext,
} from '../../types';

const API_ENDPOINT = '/user-access-tokens/{user_access_token_id}/';
const API_METHOD = 'delete';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function deleteUserAccessToken(
  authContext: AuthContext,
  user_access_token_id: paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['path']['user_access_token_id']
): Promise<CallApiReturn<ResponseTypesByStatus[keyof ResponseTypesByStatus]>> {
  const { data, response } = await callApi<
    ResponseTypesByStatus[keyof ResponseTypesByStatus]
  >({
    endpoint: API_ENDPOINT.replace(
      '{user_access_token_id}',
      user_access_token_id
    ),
    method: API_METHOD,
    authContext,
  });

  return { data, response };
}

export { deleteUserAccessToken, ResponseTypesByStatus };
