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

type RequestContentType<TOperation> = TOperation extends {
  requestBody:
    | { content: infer ContentTypes }
    | { content?: infer ContentTypes };
}
  ? keyof ContentTypes
  : never;

type ResponseContentType<TOperation> = TOperation extends {
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

type ResponseStatusCode<TOperation> = TOperation extends {
  responses: infer Responses;
}
  ? keyof Responses
  : never;

type ResponseDataTypeByStatusCode<
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

type ResponseDataType<
  TOperation,
  TResponseContentType extends ResponseContentType<TOperation> = ResponseContentType<TOperation>,
  TResponseStatusCode extends ResponseStatusCode<TOperation> = ResponseStatusCode<TOperation>,
  TResponseDataByStatus = ResponseDataTypeByStatusCode<
    TOperation,
    TResponseContentType,
    TResponseStatusCode
  >
> = TResponseDataByStatus[keyof TResponseDataByStatus];

type RequestDataType<
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
  : // whenever the generic isn't set
    { data?: {} };

type RequestParamsType<TOperation> = TOperation extends {
  parameters: infer Params;
}
  ? Params extends { query: infer U }
    ? { params: U }
    : Params extends { query?: infer U }
    ? { params?: U }
    : { params?: never }
  : // whenever the generic isn't set
    { params?: {} };

type RequestPathParamsType<TOperation> = TOperation extends {
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
  TPath extends keyof paths,
  TMethod extends keyof paths[TPath],
  TRequestContentType extends RequestContentType<paths[TPath][TMethod]>,
  TRequestData = RequestDataType<
    paths[TPath][TMethod],
    TRequestContentType
  >['data']
> = Omit<
  CallApiOptions<TRequestData>,
  'url' | 'method' | 'data' | 'params' | 'pathParams'
> &
  RequestDataType<paths[TPath][TMethod], TRequestContentType> &
  RequestParamsType<paths[TPath][TMethod]> &
  RequestPathParamsType<paths[TPath][TMethod]>;

// const a: ApiServiceParams<'/galleries/', 'post', 'application/json'> = {};

// Extract the response type for the ApiService function
type ApiServiceReturn<
  TPath extends keyof paths,
  TMethod extends keyof paths[TPath],
  TResponseContentType extends ResponseContentType<
    paths[TPath][TMethod]
  > = ResponseContentType<paths[TPath][TMethod]>,
  TResponseStatusCode extends ResponseStatusCode<
    paths[TPath][TMethod]
  > = ResponseStatusCode<paths[TPath][TMethod]>,
  TResponseDataType = ResponseDataType<
    paths[TPath][TMethod],
    TResponseContentType,
    TResponseStatusCode
  >
> = AxiosResponse<TResponseDataType>;

// Combine ApiServiceParams and ApiServiceReturn into the function type

type ApiService<
  TPath extends keyof paths,
  TMethod extends keyof paths[TPath],
  TResponseContentType extends ResponseContentType<
    paths[TPath][TMethod]
  > = ResponseContentType<paths[TPath][TMethod]>,
  TRequestContentType extends RequestContentType<
    paths[TPath][TMethod]
  > = RequestContentType<paths[TPath][TMethod]>,
  TResponseStatusCode extends ResponseStatusCode<
    paths[TPath][TMethod]
  > = ResponseStatusCode<paths[TPath][TMethod]>
> = (
  options: ApiServiceParams<TPath, TMethod, TRequestContentType>
) => ApiServiceReturn<
  TPath,
  TMethod,
  TResponseContentType,
  TResponseStatusCode
>;

function createApiService<
  TPath extends keyof paths,
  TMethod extends keyof paths[TPath] & AxiosRequestConfig['method'],
  TResponseContentType extends ResponseContentType<
    paths[TPath][TMethod]
  > = ResponseContentType<paths[TPath][TMethod]>,
  TRequestContentType extends RequestContentType<
    paths[TPath][TMethod]
  > = RequestContentType<paths[TPath][TMethod]>,
  TResponseStatusCode extends ResponseStatusCode<
    paths[TPath][TMethod]
  > = ResponseStatusCode<paths[TPath][TMethod]>,
  TRequestData extends RequestDataType<
    paths[TPath][TMethod],
    TRequestContentType
  > = RequestDataType<paths[TPath][TMethod], TRequestContentType>,
  TResponseData extends ResponseDataType<
    paths[TPath][TMethod],
    TResponseContentType,
    TResponseStatusCode
  > = ResponseDataType<
    paths[TPath][TMethod],
    TResponseContentType,
    TResponseStatusCode
  >
>(
  path: TPath,
  method: TMethod,
  requestContentType?: TRequestContentType,
  responseContentType?: TResponseContentType
): ApiService<TPath, TMethod, TRequestContentType, TResponseContentType> {
  if (!requestContentType) {
    requestContentType = Object.keys(
      openapi_schema.paths[path][method as string].requestBody.content
    )[0] as TRequestContentType;
  }
  if (!responseContentType) {
    responseContentType = Object.keys(
      openapi_schema.paths[path][method as string].responses[
        Object.keys(openapi_schema.paths[path][method as string].responses)[0]
      ].content
    )[0] as TResponseContentType;
  }

  async function call({
    pathParams,
    headers = {},
    ...rest
  }: ApiServiceParams<TPath, TMethod, TResponseContentType>): Promise<
    ApiServiceReturn<TPath, TMethod, TResponseContentType, TResponseStatusCode>
  > {
    let url: CallApiOptions<TRequestData>['url'] = path;
    if (pathParams && typeof pathParams === 'object') {
      for (const key in pathParams) {
        url = url.replace(`{${key}}`, pathParams[key]);
      }
    }

    const response = await callApi({
      url,
      method,
      headers: {
        'Content-Type': requestContentType,
        Accept: responseContentType,
        ...headers,
      },
      ...rest,
    });
    return response as AxiosResponse<TResponseData>;
  }
  return call;
}

//   responseContentType = Object.keys(
//     openapi_schema.paths[path][method as string].responses[
//       Object.keys(openapi_schema.paths[path][method as string].responses)[0]
//     ].content
//   )[0],

// function useApiCall<
//   TPath extends keyof paths,
//   TMethod extends keyof paths[TPath],
//   TResponseContentType extends ResponseContentType<paths[TPath][TMethod]>,
//   TRequestContentType extends RequestContentType<paths[TPath][TMethod]>,
// >(
//   apiService: ApiService<
//     TPath,
//     TMethod,
//     TRequestContentType,
//     TResponseContentType
//   >,
//   apiServiceOptions: ApiServiceParams<TPath, TMethod, TRequestContentType>,
//   dependencies: any[] = []
// ): UseApiCallReturn<
//   ExtractResponseTypes<paths[TPath][TMethod]>[keyof ExtractResponseTypes<
//     paths[TPath][TMethod]
//   >]
// > {
//   const [loading, setLoading] = useState<boolean>(true);
//   const [response, setResponse] =
//     useState<
//       AxiosResponse<
//         ExtractResponseTypes<paths[Path][Method]>[keyof ExtractResponseTypes<
//           paths[Path][Method]
//         >]
//       >
//     >(null);

//   async function refetch() {
//     setLoading(true);
//     const b = await apiService(apiServiceOptions);
//     setResponse(b);
//     setLoading(false);
//   }

//   useEffect(() => {
//     refetch();
//   }, dependencies);

//   return { ...response, loading, refetch };
// }

export {
  callApi,
  //   useApiCall,
  createApiService,
  ResponseContentType,
  RequestContentType,
  ResponseDataType,
  ResponseStatusCode,
  ResponseDataTypeByStatusCode,
  RequestDataType,
  RequestParamsType,
  RequestPathParamsType,
};
