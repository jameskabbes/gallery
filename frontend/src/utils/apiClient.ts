import axios from 'axios';
import qs from 'qs';
import { config } from '../config';

const apiClient = axios.create({
  baseURL: config.backendUrl,
  timeout: 10000, // 10 seconds timeout, adjust as needed,
  paramsSerializer: (params) => qs.stringify(params, { arrayFormat: 'repeat' }), // Ensure consistent array serialization
});

apiClient.interceptors.request.use((config) => {
  if (config.headers['Content-Type'] === 'application/x-www-form-urlencoded') {
    config.data = qs.stringify(config.data);
  }
  return config;
});

export { apiClient };
