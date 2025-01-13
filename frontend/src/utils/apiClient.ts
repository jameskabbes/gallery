import axios, {
  AxiosRequestConfig,
  AxiosResponse,
  AxiosError,
  AxiosProgressEvent,
} from 'axios';
import config from '../../../config.json';
import siteConfig from '../../siteConfig.json';
import qs from 'qs';

const apiClient = axios.create({
  baseURL: `/${config.api_endpoint_base}`,
  timeout: 10000, // 10 seconds timeout, adjust as needed,
  paramsSerializer: (params) => qs.stringify(params, { arrayFormat: 'repeat' }), // Ensure consistent array serialization
});

// apiClient.interceptors.request.use((requestConfig) => {
//   // Add Authorization header if token is present and not already set
//   if (!requestConfig.headers['Authorization']) {
//     const token = localStorage.getItem(siteConfig['access_token_key']);
//     if (token) {
//       requestConfig.headers['Authorization'] = `Bearer ${token}`;
//     }
//   }
//   return requestConfig;
// });

export { apiClient };
