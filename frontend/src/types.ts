import React from 'react';
import { paths, operations, components } from './openapi_schema';
import {
  AxiosProgressEvent,
  AxiosRequestConfig,
  AxiosResponse,
  Method,
} from 'axios';

interface CallApiOptions<T> {
  endpoint: string;
  method: Method;
  data?: T;
  headers?: Record<string, string>;
  onUploadProgress?: (progressEvent: AxiosProgressEvent) => void;
  onDownloadProgress?: (progressEvent: AxiosProgressEvent) => void;
  authContext?: AuthContextType;
}

type ApiResponse<T> = AxiosResponse<T>;

interface UseApiCallReturn<T> extends ApiResponse<T> {
  loading: boolean;
}

type ExtractResponseTypes<T> = {
  [K in keyof T]: T[K] extends {
    content: infer ContentTypes;
  }
    ? {
        [ContentType in keyof ContentTypes]: ContentTypes[ContentType];
      }[keyof ContentTypes]
    : never;
};

interface ValidatedInputState<T> {
  value: T;
  status: 'valid' | 'invalid' | 'loading';
  error: string | null;
}

const defaultValidatedInputState = <T>(
  defaultValue: T
): ValidatedInputState<T> => ({
  value: defaultValue,
  status: 'valid',
  error: null,
});

interface DarkModeContext {
  state: boolean;
  systemState: boolean;
  preference: 'light' | 'dark' | 'system';
  setPreference: (preference: 'light' | 'dark' | 'system') => void;
}

type AuthModalsType = 'logIn' | 'signUp' | 'logInWithEmail';

interface AuthModalsContextType {
  activeModalType: AuthModalsType | null;
  setActiveModalType: React.Dispatch<
    React.SetStateAction<AuthModalsContextType['activeModalType']>
  >;
}

interface LogInContextType {
  username: ValidatedInputState<string>;
  setUsername: React.Dispatch<
    React.SetStateAction<LogInContextType['username']>
  >;
  password: ValidatedInputState<string>;
  setPassword: React.Dispatch<
    React.SetStateAction<LogInContextType['password']>
  >;
  staySignedIn: ValidatedInputState<boolean>;
  setStaySignedIn: React.Dispatch<
    React.SetStateAction<LogInContextType['staySignedIn']>
  >;
  valid: boolean;
  setValid: React.Dispatch<React.SetStateAction<LogInContextType['valid']>>;
  loading: boolean;
  setLoading: React.Dispatch<React.SetStateAction<LogInContextType['loading']>>;
  error: string | null;
  setError: React.Dispatch<React.SetStateAction<LogInContextType['error']>>;
}

interface LogInWithEmailContextType {
  email: ValidatedInputState<string>;
  setEmail: React.Dispatch<
    React.SetStateAction<LogInWithEmailContextType['email']>
  >;
  staySignedIn: ValidatedInputState<boolean>;
  setStaySignedIn: React.Dispatch<
    React.SetStateAction<LogInWithEmailContextType['staySignedIn']>
  >;
  screen: 'email' | 'sent';
  setScreen: React.Dispatch<
    React.SetStateAction<LogInWithEmailContextType['screen']>
  >;
  valid: boolean;
  setValid: React.Dispatch<
    React.SetStateAction<LogInWithEmailContextType['valid']>
  >;
  loading: boolean;
  setLoading: React.Dispatch<
    React.SetStateAction<LogInWithEmailContextType['loading']>
  >;
}

interface SignUpContextType {
  email: ValidatedInputState<string>;
  setEmail: React.Dispatch<React.SetStateAction<SignUpContextType['email']>>;
  password: ValidatedInputState<string>;
  setPassword: React.Dispatch<
    React.SetStateAction<SignUpContextType['password']>
  >;
  confirmPassword: ValidatedInputState<string>;
  setConfirmPassword: React.Dispatch<
    React.SetStateAction<SignUpContextType['confirmPassword']>
  >;
  staySignedIn: ValidatedInputState<boolean>;
  setStaySignedIn: React.Dispatch<
    React.SetStateAction<SignUpContextType['staySignedIn']>
  >;
  valid: boolean;
  setValid: React.Dispatch<React.SetStateAction<SignUpContextType['valid']>>;
  error: string | null;
  setError: React.Dispatch<React.SetStateAction<SignUpContextType['error']>>;
  loading: boolean;
  setLoading: React.Dispatch<
    React.SetStateAction<SignUpContextType['loading']>
  >;
}

interface Modal {
  component: React.ReactNode;
  contentStyle: React.CSSProperties;
  includeExitButton: boolean;
  onExit: () => void;
  className: string;
  key: string;
}

const defaultModal: Modal = {
  component: null,
  className: '',
  onExit: () => null,
  includeExitButton: true,
  contentStyle: {},
  key: null,
};

interface GlobalModalsContextType {
  activeModal: Modal | null;
  clearModal: () => void;
  setModal: (modal: Partial<Modal>) => void;
}

interface DeviceContextType {
  isMobile: boolean;
}

interface Reducer<State, Dispatch> {
  state: State;
  dispatch: (action: Dispatch) => void;
}

interface DataContextType {
  studios: null;
}

type ToastId = string;

interface Toast {
  type: 'error' | 'info' | 'success' | 'pending';
  message: string;
}

interface ToastNoType extends Omit<Toast, 'type'> {}

interface ToastContextState {
  toasts: Map<ToastId, Toast>;
}

interface ToastReducerActionTypes {
  ADD: {
    type: 'ADD';
    payload: {
      id: ToastId;
      toast: Toast;
    };
  };
  REMOVE: {
    type: 'REMOVE';
    payload: string;
  };
  UPDATE: {
    type: 'UPDATE';
    payload: {
      id: ToastId;
      toast: Partial<Toast>;
    };
  };
  CLEAR: {
    type: 'CLEAR';
  };
}

type ToastReducerAction =
  ToastReducerActionTypes[keyof ToastReducerActionTypes];

interface ToastContextType {
  state: ToastContextState;
  dispatch: React.Dispatch<ToastReducerAction>;
  make: (toast: Toast) => ToastId;
  makePending: (toast: ToastNoType) => ToastId;
  update: (id: ToastId, toast: Partial<Toast>) => void;
}

type AuthContextState = components['schemas']['GetAuthBaseReturn'];

interface AuthContextType {
  state: AuthContextState;
  setState: React.Dispatch<React.SetStateAction<AuthContextState>>;
  logOut: (toastId?: ToastId) => void;
  updateFromApiResponse: (data: any) => void;
}

interface EscapeKeyContextType {
  addCallback: (callback: () => void) => void;
  removeCallback: (callback: () => void) => void;
}

interface ConfirmationModal {
  title: string;
  message: string;
  onConfirm: () => void;
  onCancel?: () => void;
  confirmText?: string;
  cancelText?: string;
  showCancel?: boolean;
}

interface SurfaceContextValue {
  level: number;
  mode: 'a' | 'b';
}

export {
  ExtractResponseTypes,
  CallApiOptions,
  ApiResponse,
  UseApiCallReturn,
  DarkModeContext,
  ValidatedInputState,
  defaultValidatedInputState,
  SignUpContextType,
  LogInContextType,
  LogInWithEmailContextType,
  Toast,
  ToastId,
  ToastNoType,
  ToastContextState,
  ToastReducerActionTypes,
  ToastReducerAction,
  ToastContextType,
  AuthContextState,
  AuthContextType,
  DeviceContextType,
  Modal,
  defaultModal,
  GlobalModalsContextType,
  AuthModalsContextType,
  AuthModalsType,
  DataContextType,
  EscapeKeyContextType,
  ConfirmationModal,
  SurfaceContextValue,
};
