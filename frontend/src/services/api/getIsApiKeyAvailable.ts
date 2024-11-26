import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import {
  ApiResponse,
  AuthContextType,
  ExtractResponseTypes,
} from '../../types';

const API_ENDPOINT = '/api-keys/available/check/';
const API_METHOD = 'get';

type GetIsApiKeyAvailableResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function getIsApiKeyAvailable(
  authContext: AuthContextType,
  apiKeyAvailable: paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['query']
): Promise<
  ApiResponse<
    GetIsApiKeyAvailableResponses[keyof GetIsApiKeyAvailableResponses]
  >
> {
  return await callApi<
    GetIsApiKeyAvailableResponses[keyof GetIsApiKeyAvailableResponses],
    paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['query']
  >({
    url: API_ENDPOINT,
    method: API_METHOD,
    params: apiKeyAvailable,
    authContext: authContext,
  });
}

async function isApiKeyAvailable(
  authContext: AuthContextType,
  apiKeyAvailable: paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['query']
): Promise<boolean> {
  const response = await getIsApiKeyAvailable(authContext, apiKeyAvailable);
  if (response.status == 200) {
    return true;
  } else {
    return false;
  }
}

export { getIsApiKeyAvailable, isApiKeyAvailable };
