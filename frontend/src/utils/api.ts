import { useState, useEffect } from 'react';
import { AxiosRequestConfig, AxiosResponse } from 'axios';
import { apiClient } from './apiClient';
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

    console.log(requestConfig);
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

type RequestContentType<TOperation> = TOperation extends {
  requestBody:
    | { content: infer ContentTypes }
    | { content?: infer ContentTypes };
}
  ? keyof ContentTypes
  : never;

type ExtractRequestDataType<
  TOperation,
  TContentType extends RequestContentType<TOperation> = RequestContentType<TOperation>
> = TOperation extends {
  requestBody: infer RequestBody;
}
  ? RequestBody extends { content: infer ContentTypes }
    ? { data: ContentTypes[keyof ContentTypes & TContentType] }
    : RequestBody extends { content?: infer ContentTypes }
    ? { data?: ContentTypes[keyof ContentTypes & TContentType] }
    : { data?: never }
  : // whenever the generic isn't set
    { data?: {} };

type ExtractRequestParamsType<TOperation> = TOperation extends {
  parameters: infer Params;
}
  ? Params extends { query: infer U }
    ? { params: U }
    : Params extends { query?: infer U }
    ? { params?: U }
    : { params?: never }
  : // whenever the generic isn't set
    { params?: {} };

type ExtractRequestPathParamsType<TOperation> = TOperation extends {
  parameters: infer Params;
}
  ? Params extends { path: infer U }
    ? { pathParams: U }
    : Params extends { path?: infer U }
    ? { pathParams?: U }
    : { pathParams?: never }
  : // whenever the generic isn't set
    { pathParams?: {} };

// Extract the parameters type for the ApiService function
type ApiServiceParams<
  Path extends keyof paths,
  Method extends keyof paths[Path],
  TRequestContentType extends RequestContentType<
    paths[Path][Method]
  > = RequestContentType<paths[Path][Method]>,
  TRequestData = ExtractRequestDataType<
    paths[Path][Method],
    TRequestContentType
  >['data'],
  TPathParams =
    | ExtractRequestPathParamsType<paths[Path][Method]>['pathParams']
    | {}
> = Omit<
  CallApiOptions<TRequestData>,
  'url' | 'method' | 'data' | 'params' | 'pathParams'
> &
  ExtractRequestDataType<paths[Path][Method], TRequestContentType> &
  ExtractRequestParamsType<paths[Path][Method]> &
  ExtractRequestPathParamsType<paths[Path][Method]> & {
    requestContentType?: TRequestContentType;
    pathParams?: TPathParams;
  };

// const a: ApiServiceParams<'/galleries/', 'post', 'application/json'> = {};

// Extract the response type for the ApiService function
type ApiServiceResponse<
  Path extends keyof paths,
  Method extends keyof paths[Path],
  Responses = ExtractResponseTypes<paths[Path][Method]>
> = Promise<AxiosResponse<Responses[keyof Responses]>>;

// Combine ApiServiceParams and ApiServiceResponse into the function type

type ApiService<
  TPath extends keyof paths,
  TMethod extends keyof paths[TPath]
> = (
  options: ApiServiceParams<TPath, TMethod>
) => ApiServiceResponse<TPath, TMethod>;

function createApiService<
  Path extends keyof paths,
  Method extends keyof paths[Path] & AxiosRequestConfig['method'],
  TRequestContentType extends RequestContentType<
    paths[Path][Method]
  > = RequestContentType<paths[Path][Method]>,
  TRequestData = ExtractRequestDataType<
    paths[Path][Method],
    TRequestContentType
  >['data'],
  Responses = ExtractResponseTypes<paths[Path][Method]>,
  TResponseData = Responses[keyof Responses]
>(path: Path, method: Method): ApiService<Path, Method> {
  async function call({
    pathParams,
    requestContentType = Object.keys(
      openapi_schema.paths[path][method as string].requestBody.content
    )[0] as TRequestContentType,
    headers = {},
    ...rest
  }: ApiServiceParams<Path, Method, TRequestContentType>) {
    let url: CallApiOptions<TRequestData>['url'] = path;
    for (const key in pathParams) {
      url = url.replace(`{${key}}`, pathParams[key]);
    }

    const response = await callApi<TRequestData, TResponseData>({
      url,
      method,
      headers: {
        'Content-Type': requestContentType,
        ...headers,
      },
      ...rest,
    });
    return response;
  }

  return call;
}

//   responseContentType = Object.keys(
//     openapi_schema.paths[path][method as string].responses[
//       Object.keys(openapi_schema.paths[path][method as string].responses)[0]
//     ].content
//   )[0],

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
  ExtractRequestParamsType,
  ExtractRequestPathParamsType,
};
