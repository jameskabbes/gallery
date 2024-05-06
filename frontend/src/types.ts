// extend the contents from openapi_schema.d.ts

// API Response
interface ApiResponse<T> {
  data: ApiResponseData<T>;
  status: ApiResponseStatus;
}
type ApiResponseData<T> = T | null;
type ApiResponseLoading = boolean;
type ApiResponseStatus = number | null;

type UseApiDataReturn<T> = [
  ApiResponseData<T>, //data
  React.Dispatch<React.SetStateAction<ApiResponseData<T>>>,
  ApiResponseLoading, //loading
  React.Dispatch<React.SetStateAction<ApiResponseLoading>>,
  ApiResponseStatus, //status
  React.Dispatch<React.SetStateAction<ApiResponseStatus>>
];

export {
  ApiResponse,
  ApiResponseData,
  ApiResponseLoading,
  ApiResponseStatus,
  UseApiDataReturn,
};
