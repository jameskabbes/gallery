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

interface CallApiProps<T> {
  endpoint: string;
  method: RequestInit['method'];
  data?: T;
}

interface CallApiReturn<T> {
  data: T | null;
  response: Response | null;
}

async function callApi<TResponseData, TRequestData = any>(
  props: CallApiProps<TRequestData>
): Promise<CallApiReturn<TResponseData>> {
  const init: RequestInit = {
    method: props.method,
    headers: {
      'Content-Type': 'application/json',
    },
    body: props.data ? JSON.stringify(props.data) : null,
  };
  const response = await callApiBase(props.endpoint, init);
  return { data: await response.json(), response };
}

function convertBackendSlugToEndpoint(slug: string): string {
  return `/${config.api_endpoint_base}${slug}`;
}

async function callBackendApi<TResponeData, TRequestData = any>(
  props: CallApiProps<TRequestData>
): Promise<CallApiReturn<TResponeData>> {
  return await callApi<TResponeData, TRequestData>({
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

function useApiCall<TResponseData, TRequestData = any>(
  props: CallApiProps<TRequestData>
): UseApiCallReturn<TResponseData> {
  const [data, setData] =
    useState<UseApiCallReturn<TResponseData>['data']>(null);
  const [loading, setLoading] =
    useState<UseApiCallReturn<TResponseData>['loading']>(true);
  const [response, setResponse] =
    useState<UseApiCallReturn<TResponseData>['response']>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      const { data, response } = await callApi<TResponseData, TRequestData>(
        props
      );
      setResponse(response);
      setData(data);
      setLoading(false);
    };

    fetchData();
  }, [props.endpoint]);

  return { data, setData, loading, setLoading, response, setResponse };
}

function useBackendApiCall<TResponseData, TRequestData = any>(
  props: CallApiProps<TRequestData>
): UseApiCallReturn<TResponseData> {
  return useApiCall<TResponseData, TRequestData>({
    ...props,
    endpoint: convertBackendSlugToEndpoint(props.endpoint),
  });
}

export { callApiBase, callApi, callBackendApi, useApiCall, useBackendApiCall };
