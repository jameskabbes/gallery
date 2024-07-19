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

interface ConfirmationModalContextState {
  isActive: boolean;
  isConfirmed: boolean | null;
  title: string | null;
  message: string | null;
}

type ConfirmationModalContextAction =
  | { type: 'SET_IS_ACTIVE'; payload: boolean }
  | { type: 'CONFIRM' }
  | { type: 'CANCEL' }
  | { type: 'RESET' }
  | { type: 'SET_TITLE'; payload: string }
  | { type: 'SET_MESSAGE'; payload: string };

interface ConfirmationModalContext {
  state: ConfirmationModalContextState;
  dispatch: (action: ConfirmationModalContextAction) => void;
}

interface ToastContext {
  toasts: string[];
}

//
type Studios = Map<
  components['schemas']['StudioID'],
  components['schemas']['StudioPublic']
>;

type StudiosReducerState = Studios;
type StudiosReducerAction =
  | { type: 'SET'; payload: Studios }
  | {
      type: 'ADD';
      payload: components['schemas']['StudioPublic'];
    }
  | { type: 'DELETE'; payload: components['schemas']['StudioID'] };

interface Reducer<State, Dispatch> {
  state: State;
  dispatch: (action: Dispatch) => void;
}

interface DataContext {
  studios: Reducer<StudiosReducerState, StudiosReducerAction>;
}

export {
  ApiResponse,
  ApiResponseData,
  ApiResponseLoading,
  ApiResponseStatus,
  UseApiDataReturn,
  ExtractResponseTypes,
  DarkModeContext,
  ConfirmationModalContextState,
  ConfirmationModalContextAction,
  ConfirmationModalContext,
  StudiosReducerState,
  StudiosReducerAction,
  DataContext,
  ToastContext,
  Studios,
};
