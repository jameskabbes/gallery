import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/Api';
import { paths, operations, components } from '../../openapi_schema';
import { AuthContext, CallApiReturn, ExtractResponseTypes } from '../../types';

const API_ENDPOINT = '/api-keys/{api_key_id}/generate-jwt/';
const API_METHOD = 'get';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function getAPIKeyJWT(
  authContext: AuthContext,
  apiKeyId: components['schemas']['APIKey']['id']
): Promise<CallApiReturn<ResponseTypesByStatus[keyof ResponseTypesByStatus]>> {
  const { data, response } = await callApi<
    ResponseTypesByStatus[keyof ResponseTypesByStatus]
  >({
    endpoint: API_ENDPOINT.replace('{api_key_id}', apiKeyId),
    method: API_METHOD,
    authContext: authContext,
  });

  return { data, response };
}

export { getAPIKeyJWT, ResponseTypesByStatus };
