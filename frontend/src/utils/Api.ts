import { useState, useEffect } from 'react';
import config from '../../../config.json';

//utility func to make API calls
async function callApiBase<T>(
  resource: RequestInfo | URL,
  options?: RequestInit
): Promise<Response> {
  console.log(options.method, resource);

  try {
    return await fetch(resource, options);
  } catch (error) {
    console.error('API Call failed:', error);
    throw error;
  }
}

interface CallProps<T> {
  endpoint: string;
  method: RequestInit['method'];
  data?: T;
}

async function callApi<T>(props: CallProps<T>): Promise<Response> {
  const init: RequestInit = {
    method: props.method,
    headers: {
      'Content-Type': 'application/json',
    },
    body: props.data ? JSON.stringify(props.data) : null,
  };

  const info: RequestInfo = props.endpoint;
  return await callApiBase(info, init);
}

function convertBackendSlugToEndpoint(slug: string): string {
  return `/${config.api_endpoint_base}${slug}`;
}

async function callBackendApi<T>(props: CallProps<T>): Promise<Response> {
  return await callApi<T>({
    ...props,
    endpoint: convertBackendSlugToEndpoint(props.endpoint),
  });
}

interface UseApiCallReturn<T> {
  data: T | null;
  setData: React.Dispatch<React.SetStateAction<UseApiCallReturn<T>['data']>>;
  loading: boolean;
  setLoading: React.Dispatch<
    React.SetStateAction<UseApiCallReturn<T>['loading']>
  >;
  response: Response | null;
  setResponse: React.Dispatch<
    React.SetStateAction<UseApiCallReturn<T>['response']>
  >;
}

function useApiCall<T>(props: CallProps<T>): UseApiCallReturn<T> {
  const [data, setData] = useState<UseApiCallReturn<T>['data']>(null);
  const [loading, setLoading] = useState<UseApiCallReturn<T>['loading']>(true);
  const [response, setResponse] =
    useState<UseApiCallReturn<T>['response']>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      const response = await callApi<T>(props);
      setResponse(response);
      setData(await response.json());
      setLoading(false);
    };

    fetchData();
  }, [props.endpoint]);

  return { data, setData, loading, setLoading, response, setResponse };
}

function useBackendApiCall<T>(props: CallProps<T>): UseApiCallReturn<T> {
  return useApiCall<T>({
    ...props,
    endpoint: convertBackendSlugToEndpoint(props.endpoint),
  });
}

export { callApiBase, callApi, callBackendApi, useApiCall, useBackendApiCall };
