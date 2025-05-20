import { useState, useEffect } from 'react';
import { AxiosRequestConfig, AxiosResponse } from 'axios';
import { apiClient } from './apiClient';
import { AuthContextType, CallApiOptions, UseApiCallReturn } from '../types';
import { paths, operations, components } from '../openapi_schema';
import openapi_schema from '../../../openapi_schema.json';
import { config } from '../config/config';

function handleAuthContext<T>(
  authContext: AuthContextType,
  headers: AxiosResponse['headers'],
  data: T
) {
  if (authContext && headers[config.headerKeys['auth_logout']]) {
    authContext.logOut();
  }
  if (authContext) {
    authContext.updateFromApiResponse(data);
  }
}

export async function callApi<TResponseData, TRequestData = any>({
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
    console.log('Response headers:', response.headers);

    handleAuthContext<TResponseData>(
      authContext,
      response.headers,
      response.data
    );

    return response;
  } catch (error) {
    console.log(error);
    handleAuthContext<TResponseData>(
      authContext,
      error.response?.headers,
      error.response?.data
    );
    return error.response;
  }
}

export type RequestContentType<TOperation> = TOperation extends {
  requestBody:
    | { content: infer ContentTypes }
    | { content?: infer ContentTypes };
}
  ? keyof ContentTypes
  : never;

export type ResponseContentType<TOperation> = TOperation extends {
  responses: infer Responses;
}
  ? {
      [StatusCode in keyof Responses]: Responses[StatusCode] extends {
        content: infer ContentTypes;
      }
        ? keyof ContentTypes
        : never;
    }[keyof Responses]
  : never;

export type ResponseStatusCode<TOperation> = TOperation extends {
  responses: infer Responses;
}
  ? keyof Responses
  : never;

export type ResponseDataTypeByStatusCode<
  TOperation,
  TResponseContentType extends ResponseContentType<TOperation> = ResponseContentType<TOperation>,
  TResponseStatusCode extends ResponseStatusCode<TOperation> = ResponseStatusCode<TOperation>
> = TOperation extends {
  responses: infer Responses;
}
  ? {
      [K in keyof Responses]: K extends TResponseStatusCode
        ? Responses[K] extends {
            content: infer ContentTypes;
          }
          ? TResponseContentType extends keyof ContentTypes
            ? ContentTypes[TResponseContentType]
            : never
          : never
        : never;
    }
  : never;

export type ResponseDataType<
  TOperation,
  TResponseContentType extends ResponseContentType<TOperation> = ResponseContentType<TOperation>,
  TResponseStatusCode extends ResponseStatusCode<TOperation> = ResponseStatusCode<TOperation>,
  TResponseDataByStatus = ResponseDataTypeByStatusCode<
    TOperation,
    TResponseContentType,
    TResponseStatusCode
  >
> = TResponseDataByStatus[keyof TResponseDataByStatus];

export type RequestDataTypeProp<
  TOperation,
  TRequestContentType extends RequestContentType<TOperation> = RequestContentType<TOperation>
> = TOperation extends {
  requestBody: infer RequestBody;
}
  ? RequestBody extends { content: infer ContentTypes }
    ? { data: ContentTypes[keyof ContentTypes & TRequestContentType] }
    : RequestBody extends { content?: infer ContentTypes }
    ? { data?: ContentTypes[keyof ContentTypes & TRequestContentType] }
    : { data?: never }
  : TOperation extends { requestBody?: infer RequestBody }
  ? RequestBody extends
      | { content: infer ContentTypes }
      | { content?: infer ContentTypes }
    ? { data?: ContentTypes[keyof ContentTypes & TRequestContentType] }
    : { data?: never }
  : { data?: never };

export type RequestDataType<
  TOperation,
  TRequestContentType extends RequestContentType<TOperation> = RequestContentType<TOperation>
> = RequestDataTypeProp<TOperation, TRequestContentType>['data'];

export type RequestParamsTypeProp<TOperation> = TOperation extends {
  parameters: infer Params;
}
  ? Params extends { query: infer U }
    ? { params: U }
    : Params extends { query?: infer U }
    ? { params?: U }
    : { params?: never }
  : // whenever the generic isn't set
    { params?: never };

export type RequestParamsType<TOperation> =
  RequestParamsTypeProp<TOperation>['params'];

export type RequestPathParamsTypeProp<TOperation> = TOperation extends {
  parameters: infer Params;
}
  ? Params extends { path: infer U }
    ? { pathParams: U }
    : Params extends { path?: infer U }
    ? { pathParams?: U }
    : { pathParams?: never }
  : // whenever the generic isn't set
    { pathParams?: never };

export type RequestPathParamsType<TOperation> =
  RequestPathParamsTypeProp<TOperation>['pathParams'];

// Extract the parameters type for the ApiService function
export type ApiServiceCallParams<
  TPath extends keyof paths,
  TMethod extends keyof paths[TPath],
  TRequestContentType extends RequestContentType<paths[TPath][TMethod]>,
  TRequestData
> = Omit<
  CallApiOptions<TRequestData>,
  'url' | 'method' | 'data' | 'params' | 'pathParams'
> &
  RequestDataTypeProp<paths[TPath][TMethod], TRequestContentType> &
  RequestParamsTypeProp<paths[TPath][TMethod]> &
  RequestPathParamsTypeProp<paths[TPath][TMethod]>;

export type ApiService<
  TPath extends keyof paths,
  TMethod extends keyof paths[TPath],
  TResponseContentType extends ResponseContentType<paths[TPath][TMethod]>,
  TResponseStatusCode extends ResponseStatusCode<paths[TPath][TMethod]>,
  TResponseDataByStatus extends ResponseDataTypeByStatusCode<
    paths[TPath][TMethod],
    TResponseContentType,
    TResponseStatusCode
  >,
  TResponseDataType extends ResponseDataType<
    paths[TPath][TMethod],
    TResponseContentType,
    TResponseStatusCode
  >,
  TRequestContentType extends RequestContentType<paths[TPath][TMethod]>,
  TRequestDataType extends RequestDataType<
    paths[TPath][TMethod],
    TRequestContentType
  >
> = {
  call: (
    options: ApiServiceCallParams<
      TPath,
      TMethod,
      TRequestContentType,
      TRequestDataType
    >
  ) => Promise<AxiosResponse<TResponseDataType>>;
  responses: TResponseDataByStatus;
};

export function createApiService<
  TPath extends keyof paths,
  TMethod extends keyof paths[TPath] & AxiosRequestConfig['method'],
  TResponseContentType extends ResponseContentType<
    paths[TPath][TMethod]
  > = ResponseContentType<paths[TPath][TMethod]>,
  TResponseStatusCode extends ResponseStatusCode<
    paths[TPath][TMethod]
  > = ResponseStatusCode<paths[TPath][TMethod]>,
  TResponseDataByStatus extends ResponseDataTypeByStatusCode<
    paths[TPath][TMethod],
    TResponseContentType,
    TResponseStatusCode
  > = ResponseDataTypeByStatusCode<
    paths[TPath][TMethod],
    TResponseContentType,
    TResponseStatusCode
  >,
  TResponseData extends ResponseDataType<
    paths[TPath][TMethod],
    TResponseContentType,
    TResponseStatusCode
  > = ResponseDataType<
    paths[TPath][TMethod],
    TResponseContentType,
    TResponseStatusCode
  >,
  TRequestContentType extends RequestContentType<
    paths[TPath][TMethod]
  > = RequestContentType<paths[TPath][TMethod]>,
  TRequestData extends RequestDataType<
    paths[TPath][TMethod],
    TRequestContentType
  > = RequestDataType<paths[TPath][TMethod], TRequestContentType>
>(
  path: TPath,
  method: TMethod,
  requestContentType?: TRequestContentType,
  responseContentType?: TResponseContentType
): ApiService<
  TPath,
  TMethod,
  TResponseContentType,
  TResponseStatusCode,
  TResponseDataByStatus,
  TResponseData,
  TRequestContentType,
  TRequestData
> {
  // default to find the content type from the first request content
  if (!requestContentType) {
    requestContentType = openapi_schema.paths[path][method as string]
      ?.requestBody?.content
      ? (Object.keys(
          openapi_schema.paths[path][method as string].requestBody.content
        )[0] as TRequestContentType)
      : null;
  }

  // default to find the content type from the first request content
  if (!responseContentType) {
    responseContentType = openapi_schema.paths[path][method as string]
      .responses[
      Object.keys(openapi_schema.paths[path][method as string].responses)[0]
    ]?.content
      ? (Object.keys(
          openapi_schema.paths[path][method as string].responses[
            Object.keys(
              openapi_schema.paths[path][method as string].responses
            )[0]
          ].content
        )[0] as TResponseContentType)
      : null;
  }

  const call = async ({
    pathParams,
    headers = {},
    ...rest
  }: ApiServiceCallParams<
    TPath,
    TMethod,
    TRequestContentType,
    TRequestData
  >) => {
    let url: CallApiOptions<TRequestData>['url'] = path;
    if (pathParams && typeof pathParams === 'object') {
      for (const key in pathParams) {
        url = url.replace(`{${key}}`, pathParams[key]);
      }
    }

    const r = await callApi<TResponseData, TRequestData>({
      url,
      method,
      headers: {
        ...(requestContentType ? { 'Content-Type': requestContentType } : {}),
        ...(responseContentType ? { Accept: responseContentType } : {}),
        ...headers,
      },
      ...rest,
    });
    return r;
  };

  return {
    call,
    responses: null,
  };
}

export function useApiCall<
  TPath extends keyof paths,
  TMethod extends keyof paths[TPath] & AxiosRequestConfig['method'],
  TResponseContentType extends ResponseContentType<paths[TPath][TMethod]>,
  TRequestContentType extends RequestContentType<paths[TPath][TMethod]>,
  TResponseStatusCode extends ResponseStatusCode<paths[TPath][TMethod]>,
  TRequestData extends RequestDataType<
    paths[TPath][TMethod],
    TRequestContentType
  >,
  TResponseData extends ResponseDataType<
    paths[TPath][TMethod],
    TResponseContentType,
    TResponseStatusCode
  >,
  TResponseDataByStatus extends ResponseDataTypeByStatusCode<
    paths[TPath][TMethod],
    TResponseContentType,
    TResponseStatusCode
  >
>(
  apiService: ApiService<
    TPath,
    TMethod,
    TResponseContentType,
    TResponseStatusCode,
    TResponseDataByStatus,
    TResponseData,
    TRequestContentType,
    TRequestData
  >,
  apiServiceOptions: ApiServiceCallParams<
    TPath,
    TMethod,
    TRequestContentType,
    TResponseData
  >,
  dependencies: any[] = []
): UseApiCallReturn<TResponseData> {
  const [loading, setLoading] = useState<boolean>(true);
  const [response, setResponse] = useState<AxiosResponse<TResponseData>>(null);

  async function refetch() {
    setLoading(true);
    const b = await apiService.call(apiServiceOptions);
    setResponse(b);
    setLoading(false);
  }

  useEffect(() => {
    refetch();
  }, dependencies);

  return { ...response, loading, refetch };
}
