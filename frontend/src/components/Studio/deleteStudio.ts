import { paths, operations, components } from '../../openapi_schema';
import { callApi } from '../../utils/Api';
import { ApiResponse, ExtractResponseTypes } from '../../types';

const API_PATH = '/studios/{studio_id}/';
const API_METHOD = 'delete';

type AllResponseTypes = ExtractResponseTypes<
  paths[typeof API_PATH][typeof API_METHOD]['responses']
>;

async function deleteStudio(studioId: components['schemas']['StudioID']) {
  callApi(API_PATH.replace('{studio_id}', studioId), API_METHOD);
}

export { deleteStudio };
