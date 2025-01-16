import axios from 'axios';
import config from '../../../config.json';
import qs from 'qs';

const apiClient = axios.create({
  baseURL: `/${config.api_endpoint_base}`,
  timeout: 10000, // 10 seconds timeout, adjust as needed,
  paramsSerializer: (params) => qs.stringify(params, { arrayFormat: 'repeat' }), // Ensure consistent array serialization
});

export { apiClient };
