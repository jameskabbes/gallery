import { useState, useEffect } from 'react';
import siteConfig from '../../siteConfig.json';
import {
  ApiResponse,
  ApiResponseData,
  ApiResponseLoading,
  ApiResponseStatus,
  UseApiDataReturn,
} from '../types';

//utility func to make API calls
async function callApi<T>(
  endpoint: string,
  method = 'GET',
  data = null
): Promise<ApiResponse<T>> {
  const requestOptions = {
    method,
    headers: {
      'Content-Type': 'application/json',
    },
    body: data ? JSON.stringify(data) : null,
  };

  console.log('Calling API: ' + endpoint);
  const response = await fetch(
    '/' + siteConfig.api_endpoint_base + endpoint,
    requestOptions
  );

  try {
    const responseData = await response.json();
    return { data: responseData, status: response.status };
  } catch {
    return { data: null, status: response.status };
  }
}

function useApiData<T>(endpoint: string): UseApiDataReturn<T> {
  const [apiData, setApiData] = useState<ApiResponseData<T>>(null);
  const [loading, setLoading] = useState<ApiResponseLoading>(true);
  const [status, setStatus] = useState<ApiResponseStatus>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const response = await callApi<T>(endpoint);
        setApiData(response.data);
        setStatus(response.status);
        setLoading(false);
      } catch (error) {
        console.error(error);
        setLoading(false);
      }
    }
    fetchData();
  }, [endpoint]);

  return [apiData, setApiData, loading, setLoading, status, setStatus];
}

export { callApi, useApiData };
