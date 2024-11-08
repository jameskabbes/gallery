import { callApi } from '../../utils/Api';
import { paths, operations, components } from '../../openapi_schema';
import {
  AuthContext,
  CallApiReturn,
  ExtractResponseTypes,
  ToastContext,
} from '../../types';

const API_ENDPOINT = '/api-keys/{api_key_id}/';
const API_METHOD = 'patch';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function patchApiKey(
  authContext: AuthContext,
  apiKeyID: components['schemas']['ApiKey']['id'],
  apiKeyUpdate: paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
): Promise<CallApiReturn<ResponseTypesByStatus[keyof ResponseTypesByStatus]>> {
  const { data, response } = await callApi<
    ResponseTypesByStatus[keyof ResponseTypesByStatus],
    paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
  >({
    endpoint: API_ENDPOINT.replace('{api_key_id}', apiKeyID),
    method: API_METHOD,
    data: apiKeyUpdate,
    authContext,
  });

  return { data, response };
}

export { patchApiKey, ResponseTypesByStatus };
