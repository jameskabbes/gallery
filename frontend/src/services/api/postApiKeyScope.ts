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

async function postApiKeyScope(
  authContext: AuthContext,
  apiKeyId: paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['path']['api_key_id'],
  scopeId: paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['path']['scope_id']
): Promise<CallApiReturn<ResponseTypesByStatus[keyof ResponseTypesByStatus]>> {
  const { data, response } = await callApi<
    ResponseTypesByStatus[keyof ResponseTypesByStatus],
    paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['path']
  >({
    endpoint: API_ENDPOINT.replace('{api_key_id}', apiKeyId).replace(
      '{scope_id}',
      scopeId.toString()
    ),
    method: API_METHOD,
    authContext,
  });

  return { data, response };
}

export { postApiKeyScope, ResponseTypesByStatus };
