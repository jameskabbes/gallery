import axios, {
  AxiosRequestConfig,
  AxiosResponse,
  AxiosError,
  AxiosProgressEvent,
} from 'axios';
import config from '../../../config.json';
import siteConfig from '../../siteConfig.json';

const apiClient = axios.create({
  baseURL: `/${config.api_endpoint_base}`,
  timeout: 10000, // 10 seconds timeout, adjust as needed
});

apiClient.interceptors.request.use((requestConfig) => {
  // Add Authorization header if token is present and not already set
  if (!requestConfig.headers['Authorization']) {
    const token = localStorage.getItem(siteConfig['access_token_key']);
    if (token) {
      requestConfig.headers['Authorization'] = `Bearer ${token}`;
    }
  }
  return requestConfig;
});

export { apiClient };
