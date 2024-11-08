import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/Api';
import { paths, operations, components } from '../../openapi_schema';
import { CallApiReturn, ExtractResponseTypes, ToastContext } from '../../types';
import { AuthContext } from '../../types';

const API_ENDPOINT = '/api-keys/{api_key_id}/';
const API_METHOD = 'delete';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function deleteApiKey(
  authContext: AuthContext,
  api_key_id: paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['path']['api_key_id']
): Promise<CallApiReturn<ResponseTypesByStatus[keyof ResponseTypesByStatus]>> {
  const { data, response } = await callApi<
    ResponseTypesByStatus[keyof ResponseTypesByStatus]
  >({
    endpoint: API_ENDPOINT.replace('{api_key_id}', api_key_id),
    method: API_METHOD,
    authContext,
  });

  return { data, response };
}

export { deleteApiKey, ResponseTypesByStatus };
