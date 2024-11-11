import axios, { AxiosRequestConfig, AxiosResponse } from 'axios';

import { useState, useEffect, useContext } from 'react';
import config from '../../../config.json';
import siteConfig from '../../siteConfig.json';
import { AuthContext } from '../contexts/Auth';
import { CallApiProps, CallApiReturn, UseApiCallReturn } from '../types';

//utility func to make API calls

async function callApiBase(
  resource: string,
  options: AxiosRequestConfig = {},
  backend: boolean = true
): Promise<AxiosResponse> {
  if (backend) {
    resource = `/${config.api_endpoint_base}${resource}`;
  }
  try {
    const response = await axios({ url: resource, ...options });
    return response;
  } catch (error) {
    console.error('API Call failed:', error);
    throw error;
  }
}

// async function callApi<TResponseData extends object, TRequestData = any>({
//   endpoint,
//   method,
//   authContext,
//   data,
//   overwriteHeaders = {},
//   body,
//   backend = true,
// }: CallApiProps<TRequestData>): Promise<CallApiReturn<TResponseData>> {
//   const token = localStorage.getItem(siteConfig['access_token_key']);

//   const headers: RequestInit['headers'] = {
//     Authorization: token ? `Bearer ${token}` : '',
//   };

//   if (data && !body) {
//     headers['Content-Type'] = 'application/json';
//   }

//   const init: RequestInit = {
//     method: method.toUpperCase(),
//     headers: { ...headers, ...overwriteHeaders },
//     body: body ? body : data ? JSON.stringify(data) : null,
//   };

//   const response = await callApiBase(endpoint, init, backend);
//   let responseData: CallApiReturn<TResponseData>['data'] = null;

//   try {
//     responseData = await response.json();
//   } catch (error) {
//     responseData = null;
//   }

//   if (authContext && response.headers.has(config.header_keys['auth_error'])) {
//     authContext.logOut();
//   }

//   return { data: responseData, response };
// }

async function callApi<TResponseData, TRequestData = any>({
  endpoint,
  method,
  authContext,
  data,
  overwriteHeaders = {},
  body,
  backend = true,
}: CallApiProps<TRequestData>): Promise<CallApiReturn<TResponseData>> {
  const token = localStorage.getItem(siteConfig['access_token_key']);

  const headers: Record<string, string> = {
    Authorization: token ? `Bearer ${token}` : '',
    ...overwriteHeaders,
  };

  const options = {
    method: method.toUpperCase(),
    headers,
    data: body || data,
    url: endpoint,
  };

  const response = await callApiBase(endpoint, options, backend);
  const responseData = response.data;

  if (authContext && response.headers[config.header_keys['auth_error']]) {
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
