import { callApi } from '../../utils/Api';
import { paths, operations, components } from '../../openapi_schema';
import {
  AuthContext,
  CallApiReturn,
  ExtractResponseTypes,
  ToastContext,
} from '../../types';

const API_ENDPOINT = '/galleries/{gallery_id}/';
const API_METHOD = 'patch';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function patchAPIKey(
  authContext: AuthContext,
  galleryId: components['schemas']['APIKey']['id'],
  galleryUpdate: paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
): Promise<CallApiReturn<ResponseTypesByStatus[keyof ResponseTypesByStatus]>> {
  const { data, response } = await callApi<
    ResponseTypesByStatus[keyof ResponseTypesByStatus],
    paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
  >({
    endpoint: API_ENDPOINT.replace('{gallery_id}', galleryId),
    method: API_METHOD,
    data: galleryUpdate,
    authContext,
  });

  return { data, response };
}

export { patchAPIKey, ResponseTypesByStatus };
