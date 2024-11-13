import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import {
  ApiResponse,
  AuthContextType,
  ExtractResponseTypes,
} from '../../types';

const API_ENDPOINT = '/api-keys/{api_key_id}/scopes/{scope_id}/';
const API_METHOD = 'delete';

type DeleteApiKeyScopeResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function deleteApiKeyScope(
  authContext: AuthContextType,
  apiKeyId: paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['path']['api_key_id'],
  scopeId: paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['path']['scope_id']
): Promise<
  ApiResponse<DeleteApiKeyScopeResponses[keyof DeleteApiKeyScopeResponses]>
> {
  return await callApi<
    DeleteApiKeyScopeResponses[keyof DeleteApiKeyScopeResponses],
    paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['path']
  >({
    url: API_ENDPOINT.replace('{api_key_id}', apiKeyId).replace(
      '{scope_id}',
      scopeId.toString()
    ),
    method: API_METHOD,
    authContext,
  });
}

export { deleteApiKeyScope, DeleteApiKeyScopeResponses };
