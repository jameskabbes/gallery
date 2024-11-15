import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import {
  ApiResponse,
  AuthContextType,
  ExtractResponseTypes,
} from '../../types';

const API_ENDPOINT = '/api-keys/available/';
const API_METHOD = 'get';

type GetIsApiKeyAvailableResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function getIsApiKeyAvailable(
  authContext: AuthContextType,
  apiKeyAvailable: paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
): Promise<
  ApiResponse<
    GetIsApiKeyAvailableResponses[keyof GetIsApiKeyAvailableResponses]
  >
> {
  console.log(apiKeyAvailable);

  return await callApi<
    GetIsApiKeyAvailableResponses[keyof GetIsApiKeyAvailableResponses],
    paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
  >({
    url: API_ENDPOINT,
    method: API_METHOD,
    data: apiKeyAvailable,
    authContext: authContext,
  });
}

async function isApiKeyAvailable(
  authContext: AuthContextType,
  apiKeyAvailable: paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
): Promise<boolean> {
  const response = await getIsApiKeyAvailable(authContext, apiKeyAvailable);
  if (response.status == 200) {
    const data = response.data as GetIsApiKeyAvailableResponses['200'];
    return data.available;
  } else {
    return false;
  }
}

export { getIsApiKeyAvailable, isApiKeyAvailable };
