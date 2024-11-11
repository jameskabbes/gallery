import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import { ApiResponse, AuthContext, ExtractResponseTypes } from '../../types';

const API_ENDPOINT = '/api-keys/{api_key_id}/scopes/{scope_id}/';
const API_METHOD = 'post';

type PostApiKeyScopeResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function postApiKeyScope(
  authContext: AuthContext,
  apiKeyId: paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['path']['api_key_id'],
  scopeId: paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['path']['scope_id']
): Promise<
  ApiResponse<PostApiKeyScopeResponses[keyof PostApiKeyScopeResponses]>
> {
  return await callApi<
    PostApiKeyScopeResponses[keyof PostApiKeyScopeResponses],
    paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['path']
  >({
    endpoint: API_ENDPOINT.replace('{api_key_id}', apiKeyId).replace(
      '{scope_id}',
      scopeId.toString()
    ),
    method: API_METHOD,
    authContext,
  });
}

export { postApiKeyScope, PostApiKeyScopeResponses };
