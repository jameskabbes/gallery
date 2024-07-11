import { paths, operations, components } from '../../openapi_schema';
import { callApi } from '../../utils/Api';

const API_PATH = '/studios/{studio_id}/';

async function deleteStudio(
  studioId: paths[typeof API_PATH]['delete']['parameters']['path']['studio_id']
): {
  let a = callApi<paths[typeof API_PATH]['delete']['responses']['200']['content']['application/json']>(
    `/studios/${studioId}/`,
    'DELETE'
  );
  console.log(a);
}

export { deleteStudio };
