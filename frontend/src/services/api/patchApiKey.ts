import { callApi } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import {
  ApiResponse,
  AuthContextType,
  ExtractResponseTypes,
} from '../../types';

const API_ENDPOINT = '/api-keys/{api_key_id}/';
const API_METHOD = 'patch';

type PatchApiKeyResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function patchApiKey(
  authContext: AuthContextType,
  apiKeyID: components['schemas']['ApiKey']['id'],
  apiKeyUpdate: paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
): Promise<ApiResponse<PatchApiKeyResponses[keyof PatchApiKeyResponses]>> {
  return await callApi<
    PatchApiKeyResponses[keyof PatchApiKeyResponses],
    paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
  >({
    endpoint: API_ENDPOINT.replace('{api_key_id}', apiKeyID),
    method: API_METHOD,
    data: apiKeyUpdate,
    authContext,
  });
}

export { patchApiKey, PatchApiKeyResponses };
