import { useState, useEffect, useContext } from 'react';
import { AxiosRequestConfig, AxiosResponse } from 'axios';
import { apiClient } from './apiClient';
import { AuthContext } from '../contexts/Auth';
import { ApiResponse, CallApiOptions, UseApiCallReturn } from '../types';
import constants from '../../../constants.json';
import { paths, operations, components } from '../openapi_schema';
import { AuthContextType } from '../types';
import { FirstKey } from '../types';
import openapi_schema from '../../../openapi_schema.json';

async function callApi<TResponseData, TRequestData = any>({
  url,
  method,
  authContext = null,
  ...rest
}: CallApiOptions<TRequestData>): Promise<ApiResponse<TResponseData>> {
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

function useApiCall<TResponseData extends object, TRequestData = any>(
  props: Omit<CallApiOptions<TRequestData>, 'authContext'>,
  dependencies: any[] = []
): UseApiCallReturn<TResponseData> {
  const [loading, setLoading] = useState<boolean>(true);
  const [response, setResponse] = useState<AxiosResponse>(null);
  const authContext = useContext(AuthContext);

  const fetchData = async () => {
    const response = await callApi<TResponseData, TRequestData>({
      ...props,
      authContext: authContext,
    });
    setResponse(response);
  };

  async function refetch() {
    setLoading(true);
    await fetchData();
    setLoading(false);
  }

  useEffect(() => {
    refetch();
  }, dependencies);

  return { ...response, loading, refetch };
}

// type HasRequestBody<T> = T extends { requestBody: any } ? T : never;
// type HasParameters<T> = T extends { parameters: any } ? T : never;

// type ExtractRequestBodyContentTypes<T> = T extends {
//   requestBody: { content: infer ContentTypes };
// }
//   ? keyof ContentTypes
//   : never;

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

type ExtractRequestQueryParamsType<T> = T extends { parameters: infer Params }
  ? Params extends { query?: infer U }
    ? U
    : never
  : never;

type ExtractRequestPathParamsType<T> = T extends { parameters: infer Params }
  ? Params extends { path?: infer U }
    ? U
    : never
  : never;

type OptionalIfNever<T> = T extends [never] ? never : T;

const a: ExtractRequestPathParamsType<paths['/api-keys/{api_key_id}/']['get']> =
  {
    api_key_id: 'string',
  };

interface ApiService<
  Path extends keyof paths,
  Method extends keyof paths[Path]
> {
  call: (
    options: Omit<
      CallApiOptions<ExtractRequestDataType<paths[Path][Method]>>,
      'url' | 'method'
    > & {
      data: OptionalIfNever<ExtractRequestDataType<paths[Path][Method]>>;
      params: OptionalIfNever<
        ExtractRequestQueryParamsType<paths[Path][Method]>
      >;
      pathParams: OptionalIfNever<
        ExtractRequestPathParamsType<paths[Path][Method]>
      >;
    }
  ) => Promise<
    ApiResponse<
      ExtractResponseTypes<paths[Path][Method]>[keyof ExtractResponseTypes<
        paths[Path][Method]
      >]
    >
  >;
  responses: ExtractResponseTypes<paths[Path][Method]>;
}

function createApiService<
  Path extends keyof paths,
  Method extends keyof paths[Path] & AxiosRequestConfig['method']
>(path: Path, method: Method): ApiService<Path, Method> {
  type Responses = ExtractResponseTypes<paths[Path][Method]>;
  type TRequestData = ExtractRequestDataType<paths[Path][Method]>;
  type TResponseData = Responses[keyof Responses];

  return {
    call: async ({ pathParams = {}, ...rest }) => {
      let url: CallApiOptions<TRequestData>['url'] = path;
      for (const key in pathParams) {
        url = url.replace(`{${key}}`, pathParams[key]);
      }

      let contentType: string = null;
      const endpoint = openapi_schema.paths[path][method as string];
      if ('requestBody' in endpoint && 'content' in endpoint.requestBody) {
        contentType = Object.keys(endpoint.requestBody.content)[0];
      }

      const response = await callApi<TRequestData, TResponseData>({
        url,
        method,
        ...(contentType && { headers: { 'Content-Type': contentType } }),
        ...rest,
      });
      return response;
    },
    responses: {} as Responses,
  };
}

export { callApi, useApiCall, createApiService };
