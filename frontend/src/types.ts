import { paths, operations, components } from './openapi_schema';

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

interface DarkModeContext {
  state: boolean;
  toggle: () => void;
}

interface ConfirmationModalContext {
  isActive: boolean;
  isConfirmed: boolean | null;
  title: string | null;
  message: string | null;
  setIsActive: React.Dispatch<React.SetStateAction<boolean>>;
  confirm: () => void;
  cancel: () => void;
  reset: () => void;
  setTitle: (title: string | null) => void;
  setMessage: (message: string | null) => void;
}

interface DataContext {
  studios: Map<
    components['schemas']['StudioID'],
    components['schemas']['StudioPublic']
  >;
  addStudio: (studio: components['schemas']['StudioCreate']) => void;
  removeStudio: (studioId: components['schemas']['StudioID']) => void;
}

interface ToastContext {
  toasts: string[];
}

export {
  ApiResponse,
  ApiResponseData,
  ApiResponseLoading,
  ApiResponseStatus,
  UseApiDataReturn,
  ExtractResponseTypes,
  DarkModeContext,
  ConfirmationModalContext,
  DataContext,
  ToastContext,
};
