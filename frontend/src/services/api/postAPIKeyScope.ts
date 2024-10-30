import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/Api';
import { paths, operations, components } from '../../openapi_schema';
import {
  AuthContext,
  CallApiReturn,
  ExtractResponseTypes,
  ToastContext,
} from '../../types';

const API_ENDPOINT = '/api-keys/{api_key_id}/scopes/{scope_id}/';
const API_METHOD = 'post';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function postAPIKeyScope(
  authContext: AuthContext,
  api_key_id: paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['path']['api_key_id'],
  scope_id: paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['path']['scope_id']
): Promise<CallApiReturn<ResponseTypesByStatus[keyof ResponseTypesByStatus]>> {
  const { data, response } = await callApi<
    ResponseTypesByStatus[keyof ResponseTypesByStatus],
    paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['path']
  >({
    endpoint: API_ENDPOINT.replace('{api_key_id}', api_key_id).replace(
      '{scope_id}',
      scope_id
    ),
    method: API_METHOD,
    authContext,
  });

  return { data, response };
}

export { postAPIKeyScope, ResponseTypesByStatus };
