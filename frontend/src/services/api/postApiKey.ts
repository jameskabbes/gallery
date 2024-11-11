import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import {
  ApiResponse,
  AuthContextType,
  ExtractResponseTypes,
} from '../../types';

const API_ENDPOINT = '/api-keys/';
const API_METHOD = 'post';

type PostApiKeyResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function postApiKey(
  authContext: AuthContextType,
  apiKeyCreate: paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
): Promise<ApiResponse<PostApiKeyResponses[keyof PostApiKeyResponses]>> {
  return await callApi<
    PostApiKeyResponses[keyof PostApiKeyResponses],
    paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
  >({
    endpoint: API_ENDPOINT,
    method: API_METHOD,
    data: apiKeyCreate,
    authContext: authContext,
  });
}

export { postApiKey, PostApiKeyResponses };
