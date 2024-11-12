import { useState, useEffect, useContext } from 'react';
import { AxiosRequestConfig, AxiosResponse } from 'axios';
import { apiClient } from './apiClient';
import { AuthContext } from '../contexts/Auth';
import { ApiResponse, CallApiOptions, UseApiCallReturn } from '../types';
import config from '../../../config.json';

async function callApi<TResponseData, TRequestData = any>({
  endpoint,
  method,
  data,
  headers = {},
  authContext = null,
  onUploadProgress = null,
  onDownloadProgress = null,
}: CallApiOptions<TRequestData>): Promise<ApiResponse<TResponseData>> {
  try {
    // if user didn't set Content-Type, set it based on data type
    if (!('Content-Type' in headers)) {
      if (data instanceof FormData) {
        headers['Content-Type'] = 'multipart/form-data';
      } else if (data instanceof URLSearchParams) {
        headers['Content-Type'] = 'application/x-www-form-urlencoded';
      } else if (typeof data === 'object' && !(data instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
      }
    }
    const requestConfig: AxiosRequestConfig = {
      url: endpoint,
      method: method,
      headers: headers,
      data: data,
      onUploadProgress: onUploadProgress,
      onDownloadProgress: onDownloadProgress,
    };

    console.log(method, endpoint);
    const response = await apiClient.request<TResponseData>(requestConfig);
    if (authContext && response.headers[config.header_keys['auth_error']]) {
      authContext.logOut();
    }
    return response;
  } catch (error) {
    console.log(error);
    return error.response;
  }
}

function useApiCall<TResponseData extends object, TRequestData = any>(
  props: Omit<CallApiOptions<TRequestData>, 'authContext'>,
  dependencies: any[] = []
): UseApiCallReturn<TResponseData> {
  const [loading, setLoading] = useState<boolean>(true);
  const [response, setResponse] = useState<AxiosResponse>(null);
  const authContext = useContext(AuthContext);

  async function refetch() {
    setLoading(true);
    const fetchData = async () => {
      const response = await callApi<TResponseData, TRequestData>({
        ...props,
        authContext: authContext,
      });
      setResponse(response);
      setLoading(false);
      authContext.updateFromApiResponse(response.data);
    };
    await fetchData();
  }

  useEffect(() => {
    refetch();
  }, dependencies);

  return { ...response, loading, refetch };
}

export { callApi, useApiCall };
