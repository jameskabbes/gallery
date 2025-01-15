import { useState, useEffect, useContext } from 'react';
import { AxiosRequestConfig, AxiosResponse } from 'axios';
import { apiClient } from './apiClient';
import { AuthContext } from '../contexts/Auth';
import { CallApiOptions, UseApiCallReturn } from '../types';
import constants from '../../../constants.json';
import { paths, operations, components } from '../openapi_schema';
import openapi_schema from '../../../openapi_schema.json';

async function callApi<TResponseData, TRequestData = any>({
  url,
  method,
  authContext = null,
  ...rest
}: CallApiOptions<TRequestData>): Promise<AxiosResponse<TResponseData>> {
  try {
    const requestConfig: AxiosRequestConfig = {
      url,
      method,
      ...rest,
    };

    console.log(method, url);
    const response = await apiClient.request<TResponseData>(requestConfig);

    if (authContext && response.headers[constants.header_keys['auth_logout']]) {
      authContext.logOut();
    }
    if (authContext) {
      authContext.updateFromApiResponse(response.data);
    }

    console.log(response.data);
    return response;
  } catch (error) {
    console.log(error);
    return error.response;
  }
}

type ExtractResponseTypes<T> = T extends {
  responses: infer Responses;
}
  ? {
      [K in keyof Responses]: Responses[K] extends {
        content: infer ContentTypes;
      }
        ? {
            [ContentType in keyof ContentTypes]: ContentTypes[ContentType];
          }[keyof ContentTypes]
        : never;
    }
  : never;

type ExtractRequestDataType<T> = T extends {
  requestBody: { content: infer ContentTypes };
}
  ? {
      [K in keyof ContentTypes]: ContentTypes[K];
    }[keyof ContentTypes]
  : never;

type ExtractRequestQueryParamsType<T> = T extends { parameters?: infer Params }
  ? Params extends { query?: infer U }
    ? U
    : never
  : never;

type ExtractRequestPathParamsType<T> = T extends { parameters: infer Params }
  ? Params extends { path?: infer U }
    ? U
    : never
  : never;

type OptionalIfNever<T, Key extends keyof T> = T[Key] extends never
  ? Partial<Pick<T, Key>>
  : Pick<T, Key>;

// Extract the parameters type for the ApiService function
type ApiServiceParams<
  Path extends keyof paths,
  Method extends keyof paths[Path]
> = Omit<
  CallApiOptions<ExtractRequestDataType<paths[Path][Method]>>,
  'url' | 'method'
> &
  OptionalIfNever<
    { data: ExtractRequestDataType<paths[Path][Method]> },
    'data'
  > &
  OptionalIfNever<
    { params: ExtractRequestQueryParamsType<paths[Path][Method]> },
    'params'
  > &
  OptionalIfNever<
    { pathParams: ExtractRequestPathParamsType<paths[Path][Method]> },
    'pathParams'
  >;

// Extract the response type for the ApiService function
type ApiServiceResponse<
  Path extends keyof paths,
  Method extends keyof paths[Path]
> = AxiosResponse<
  ExtractResponseTypes<paths[Path][Method]>[keyof ExtractResponseTypes<
    paths[Path][Method]
  >]
>;

// Combine ApiServiceParams and ApiServiceResponse into the function type
type ApiService<Path extends keyof paths, Method extends keyof paths[Path]> = (
  options: ApiServiceParams<Path, Method>
) => Promise<ApiServiceResponse<Path, Method>>;

function createApiService<
  Path extends keyof paths,
  Method extends keyof paths[Path] & AxiosRequestConfig['method']
>(path: Path, method: Method): ApiService<Path, Method> {
  type Responses = ExtractResponseTypes<paths[Path][Method]>;
  type TRequestData = ExtractRequestDataType<paths[Path][Method]>;
  type TResponseData = Responses[keyof Responses];

  let contentType: string = null;
  const endpoint = openapi_schema.paths[path][method as string];
  if ('requestBody' in endpoint && 'content' in endpoint.requestBody) {
    contentType = Object.keys(endpoint.requestBody.content)[0];
  }

  return async ({ pathParams = {}, ...rest }) => {
    let url: CallApiOptions<TRequestData>['url'] = path;
    for (const key in pathParams) {
      url = url.replace(`{${key}}`, pathParams[key]);
    }

    const response = await callApi<TRequestData, TResponseData>({
      url,
      method,
      ...(contentType && { headers: { 'Content-Type': contentType } }),
      ...rest,
    });
    return response;
  };
}

function useApiCall<Path extends keyof paths, Method extends keyof paths[Path]>(
  apiService: ApiService<Path, Method>,
  apiServiceOptions: ApiServiceParams<Path, Method>,
  dependencies: any[] = []
): UseApiCallReturn<
  ExtractResponseTypes<paths[Path][Method]>[keyof ExtractResponseTypes<
    paths[Path][Method]
  >]
> {
  const [loading, setLoading] = useState<boolean>(true);
  const [response, setResponse] =
    useState<
      AxiosResponse<
        ExtractResponseTypes<paths[Path][Method]>[keyof ExtractResponseTypes<
          paths[Path][Method]
        >]
      >
    >(null);

  async function refetch() {
    setLoading(true);
    const b = await apiService(apiServiceOptions);
    setResponse(b);
    setLoading(false);
  }

  useEffect(() => {
    refetch();
  }, dependencies);

  return { ...response, loading, refetch };
}

export {
  callApi,
  useApiCall,
  createApiService,
  ExtractResponseTypes,
  ExtractRequestDataType,
  ExtractRequestQueryParamsType,
  ExtractRequestPathParamsType,
};
