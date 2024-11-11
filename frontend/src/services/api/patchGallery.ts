import { callApi } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import {
  ApiResponse,
  AuthContextType,
  ExtractResponseTypes,
} from '../../types';

const API_ENDPOINT = '/galleries/{gallery_id}/';
const API_METHOD = 'patch';

type PatchGalleryResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function patchAPIKey(
  authContext: AuthContextType,
  galleryId: paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['path']['gallery_id'],
  galleryUpdate: paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
): Promise<ApiResponse<PatchGalleryResponses[keyof PatchGalleryResponses]>> {
  return await callApi<
    PatchGalleryResponses[keyof PatchGalleryResponses],
    paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
  >({
    endpoint: API_ENDPOINT.replace('{gallery_id}', galleryId),
    method: API_METHOD,
    data: galleryUpdate,
    authContext,
  });
}

export { patchAPIKey, PatchGalleryResponses };
