import { useState, useEffect, useContext } from 'react';
import config from '../../../config.json';
import siteConfig from '../../siteConfig.json';
import { AuthContext } from '../contexts/Auth';

//utility func to make API calls

function generateCurlCommand(
  resource: RequestInfo | URL,
  options?: RequestInit
): string {
  const method = options?.method || 'GET';
  const url = typeof resource === 'string' ? resource : resource.toString();
  const headers = options?.headers || {};
  const body = options?.body || '';

  let curlCommand = `curl -X '${method}' \\\n  '${url}' \\\n`;

  for (const [key, value] of Object.entries(headers)) {
    curlCommand += `  -H '${key}: ${value}' \\\n`;
  }

  if (body) {
    curlCommand += `  -d '${body}' \\\n`;
  }

  return curlCommand.trim();
}

async function callApiBase<T>(
  resource: RequestInfo | URL,
  options?: RequestInit
): Promise<Response> {
  console.log(options.method, resource);
  console.log(generateCurlCommand(resource, options));

  console.log(resource);
  console.log(options);

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
}

interface CallApiReturn<T> {
  data: T | null;
  response: Response | null;
}

async function callApi<TResponseData extends object, TRequestData = any>(
  props: CallApiProps<TRequestData>
): Promise<CallApiReturn<TResponseData>> {
  const token = localStorage.getItem(siteConfig['access_token_key']);
  const init: RequestInit = {
    method: props.method,
    headers: {
      'Content-Type': 'application/json',
      Authorization: token ? `Bearer ${token}` : '',
      ...props.overwriteHeaders,
    },
    body: props.body
      ? props.body
      : props.data
      ? JSON.stringify(props.data)
      : null,
  };
  const response = await callApiBase(props.endpoint, init);

  let data: CallApiReturn<TResponseData>['data'] = null;
  try {
    data = await response.json();
  } catch (error) {
    data = null;
  }
  console.log('data');
  console.log(data);
  return { data, response };
}

function convertBackendSlugToEndpoint(slug: string): string {
  return `/${config.api_endpoint_base}${slug}`;
}

async function callBackendApi<TResponeData extends object, TRequestData = any>(
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

function useApiCall<TResponseData extends object, TRequestData = any>(
  props: CallApiProps<TRequestData>,
  setAuth: boolean = true
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
      if (setAuth && data && config.auth_key in data) {
        authContext.dispatch({
          type: 'UPDATE',
          payload: data[config.auth_key],
        });
      }
      setLoading(false);
    };

    fetchData();
  }, [props.endpoint]);

  return { data, setData, loading, setLoading, response, setResponse };
}

function useBackendApiCall<TResponseData extends object, TRequestData = any>(
  props: CallApiProps<TRequestData>,
  setAuth: boolean = false
): UseApiCallReturn<TResponseData> {
  return useApiCall<TResponseData, TRequestData>(
    {
      ...props,
      endpoint: convertBackendSlugToEndpoint(props.endpoint),
    },
    setAuth
  );
}

export { callApiBase, callApi, callBackendApi, useApiCall, useBackendApiCall };
