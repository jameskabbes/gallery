import { createApiService } from '../utils/api';

const getApiKey = createApiService('/api-keys/{api_key_id}/', 'get');

async function test() {
  const a = await getApiKey.call({
    pathParams: {
      api_key_id: 'string',
    },
    data: null as never,
    params: null as never,
  });
}
