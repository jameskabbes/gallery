import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import {
  ApiResponse,
  AuthContextType,
  ExtractResponseTypes,
} from '../../types';

const API_ENDPOINT = '/api-keys/{api_key_id}/';
const API_METHOD = 'delete';

type DeleteApiKeyResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function deleteApiKey(
  authContext: AuthContextType,
  apiKeyId: paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['path']['api_key_id']
): Promise<ApiResponse<DeleteApiKeyResponses[keyof DeleteApiKeyResponses]>> {
  return await callApi<DeleteApiKeyResponses[keyof DeleteApiKeyResponses]>({
    endpoint: API_ENDPOINT.replace('{api_key_id}', apiKeyId),
    method: API_METHOD,
    authContext,
  });
}

export { deleteApiKey, DeleteApiKeyResponses };
