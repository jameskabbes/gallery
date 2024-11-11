import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import {
  ApiResponse,
  AuthContextType,
  ExtractResponseTypes,
} from '../../types';

const API_ENDPOINT = '/api-keys/{api_key_id}/generate-jwt/';
const API_METHOD = 'get';

type GetApiKeyJwtResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function getApiKeyJWT(
  authContext: AuthContextType,
  apiKeyId: paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['path']['api_key_id']
): Promise<ApiResponse<GetApiKeyJwtResponses[keyof GetApiKeyJwtResponses]>> {
  return await callApi<GetApiKeyJwtResponses[keyof GetApiKeyJwtResponses]>({
    endpoint: API_ENDPOINT.replace('{api_key_id}', apiKeyId),
    method: API_METHOD,
    authContext: authContext,
  });
}

export { getApiKeyJWT, GetApiKeyJwtResponses };
