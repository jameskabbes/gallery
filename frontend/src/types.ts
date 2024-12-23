import React from 'react';
import { paths, operations, components } from './openapi_schema';
import {
  Axios,
  AxiosProgressEvent,
  AxiosRequestConfig,
  AxiosResponse,
  Method,
} from 'axios';

interface CallApiOptions<T> extends AxiosRequestConfig<T> {
  authContext?: AuthContextType;
}

type ApiResponse<T> = AxiosResponse<T>;

interface UseApiCallReturn<T> extends ApiResponse<T> {
  loading: boolean;
  refetch: () => void;
}

type ArrayElement<ArrayType extends readonly unknown[]> =
  ArrayType extends readonly (infer ElementType)[] ? ElementType : never;

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

interface DarkModeContextType {
  state: boolean;
  systemState: boolean;
  preference: 'light' | 'dark' | 'system';
  setPreference: (preference: 'light' | 'dark' | 'system') => void;
}

type AuthModalType = 'logIn' | 'signUp' | 'logInWithEmail';

interface AuthModalsContextType {
  activate: (modal: AuthModalType | null) => void;
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

interface ModalType<T = Record<string, any>> {
  key: string;
  Component: React.ComponentType<any>;
  componentProps?: T;
  contentAdditionalClassName?: string;
  includeExitButton?: boolean;
  onExit?: () => void;
}

type ModalUpdateType<T = Record<string, any>> = Partial<
  Omit<ModalType<Partial<T>>, 'key'>
> &
  Pick<ModalType<T>, 'key'>;

interface ModalsContextType {
  activeModal: ModalType | null;
  pushModals: (modals: ModalType[]) => void;
  deleteModals: (modalKeys: ModalType['key'][]) => void;
  updateModals: (modals: ModalUpdateType[]) => void;
  upsertModals: (modals: ModalType[]) => void;
  swapActiveModal: (modal: ModalType) => void;
}

interface DeviceContextType {
  isMobile: boolean;
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

interface SurfaceContextType {
  level: number;
  mode: 'a' | 'b';
}

type OrderByState = 'off' | 'asc' | 'desc';

export {
  ArrayElement,
  ExtractResponseTypes,
  CallApiOptions,
  ApiResponse,
  UseApiCallReturn,
  DarkModeContextType,
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
  ModalType,
  ModalUpdateType,
  ModalsContextType,
  AuthModalsContextType,
  AuthModalType,
  DataContextType,
  EscapeKeyContextType,
  SurfaceContextType,
  OrderByState,
};
