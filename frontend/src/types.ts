// extend the contents from openapi_schema.d.ts

// API Response
interface ApiResponse<T> {
  data: ApiResponseData<T>;
  status: ApiResponseStatus;
}
type ApiResponseData<T> = T | null;
type ApiResponseLoading = boolean;
type ApiResponseStatus = number | null;

type UseApiDataReturn<T> = {
  apiData: ApiResponseData<T>; //data
  setApiData: React.Dispatch<React.SetStateAction<ApiResponseData<T>>>;
  loading: ApiResponseLoading; //loading
  setLoading: React.Dispatch<React.SetStateAction<ApiResponseLoading>>;
  status: ApiResponseStatus; //status
  setStatus: React.Dispatch<React.SetStateAction<ApiResponseStatus>>;
};

type ExtractResponseTypes<T> = {
  [K in keyof T]: T[K] extends {
    content: { 'application/json': infer ContentType };
  }
    ? ContentType
    : never;
};

export {
  ApiResponse,
  ApiResponseData,
  ApiResponseLoading,
  ApiResponseStatus,
  UseApiDataReturn,
  ExtractResponseTypes,
};
