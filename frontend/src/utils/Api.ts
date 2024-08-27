import { useState, useEffect, useContext } from 'react';
import config from '../../../config.json';
import siteConfig from '../../siteConfig.json';
import { AuthContext } from '../contexts/Auth';

//utility func to make API calls

async function callApiBase<T>(
  resource: RequestInfo | URL,
  options?: RequestInit,
  backend: boolean = true
): Promise<Response> {
  if (backend) {
    resource = `/${config.api_endpoint_base}${resource}`;
  }
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
  overwriteHeaders?: HeadersInit;
  body?: string;
  backend?: boolean;
}

interface CallApiReturn<T> {
  data: T | null;
  response: Response | null;
}

async function callApi<TResponseData extends object, TRequestData = any>({
  endpoint,
  method,
  data,
  overwriteHeaders = {},
  body,
  backend = true,
}: CallApiProps<TRequestData>): Promise<CallApiReturn<TResponseData>> {
  const token = localStorage.getItem(siteConfig['access_token_key']);
  const init: RequestInit = {
    method: method.toUpperCase(),
    headers: {
      'Content-Type': 'application/json',
      Authorization: token ? `Bearer ${token}` : '',
      ...overwriteHeaders,
    },
    body: body ? body : data ? JSON.stringify(data) : null,
  };
  const response = await callApiBase(endpoint, init, backend);
  let responseData: CallApiReturn<TResponseData>['data'] = null;

  try {
    responseData = await response.json();
  } catch (error) {
    responseData = null;
  }
  return { data: responseData, response };
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

function useApiCall<TResponseData extends object, TRequestData = any>(
  props: CallApiProps<TRequestData>,
  updateAuth: boolean = true,
  dependencies: any[] = []
): UseApiCallReturn<TResponseData> {
  const [data, setData] =
    useState<UseApiCallReturn<TResponseData>['data']>(null);
  const [loading, setLoading] =
    useState<UseApiCallReturn<TResponseData>['loading']>(true);
  const [response, setResponse] =
    useState<UseApiCallReturn<TResponseData>['response']>(null);

  const authContext = useContext(AuthContext);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      const { data, response } = await callApi<TResponseData, TRequestData>(
        props
      );
      setResponse(response);
      setData(data);
      if (updateAuth && data && config.auth_key in data) {
        authContext.dispatch({
          type: 'UPDATE',
          payload: data[config.auth_key],
        });
      }
      setLoading(false);
    };

    fetchData();
  }, dependencies);

  return { data, setData, loading, setLoading, response, setResponse };
}

export { callApiBase, callApi, useApiCall };
