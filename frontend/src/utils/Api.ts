import { useState, useEffect, useContext } from 'react';
import config from '../../../config.json';
import siteConfig from '../../siteConfig.json';
import { AuthContext } from '../contexts/Auth';
import { CallApiProps, CallApiReturn, UseApiCallReturn } from '../types';

//utility func to make API calls

async function callApiBase(
  resource: RequestInfo | URL,
  options: RequestInit,
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

async function callApi<TResponseData extends object, TRequestData = any>({
  endpoint,
  method,
  authContext,
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

  if (authContext && response.headers.has(config.header_keys['auth_error'])) {
    authContext.logOut();
  }

  return { data: responseData, response };
}

function useApiCall<TResponseData extends object, TRequestData = any>(
  props: Omit<CallApiProps<TRequestData>, 'authContext'>,
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
      const { data, response } = await callApi<TResponseData, TRequestData>({
        ...props,
        authContext: authContext,
      });
      setResponse(response);
      setData(data);
      authContext.updateFromApiResponse(data);
      setLoading(false);
    };

    fetchData();
  }, dependencies);

  return { data, setData, loading, setLoading, response, setResponse };
}

export { callApiBase, callApi, useApiCall };
