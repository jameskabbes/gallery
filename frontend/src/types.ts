import React from 'react';
import { paths, operations, components } from './openapi_schema';

interface CallApiProps<T> {
  endpoint: string;
  method: RequestInit['method'];
  data?: T;
  overwriteHeaders?: HeadersInit;
  body?: string;
  backend?: boolean;
}

interface CallApiReturn<T> {
  data: T | null;
  response: Response | null;
}

interface UseApiCallReturn<T> {
  data: T | null;
  setData: React.Dispatch<React.SetStateAction<UseApiCallReturn<T>['data']>>;
  loading: boolean;
  setLoading: React.Dispatch<
    React.SetStateAction<UseApiCallReturn<T>['loading']>
  >;
  response: Response | null;
  setResponse: React.Dispatch<
    React.SetStateAction<UseApiCallReturn<T>['response']>
  >;
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

type InputStatus = 'valid' | 'invalid' | 'loading';

type InputValue = string | number | readonly string[];

interface InputState<T> {
  value: T;
  status: InputStatus;
  error: string | null;
}

const defaultInputState = <T>(defaultValue: T): InputState<T> => ({
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

interface AuthModalsContext {
  activeModalType: AuthModalsType | null;
  setActiveModalType: React.Dispatch<
    React.SetStateAction<AuthModalsContext['activeModalType']>
  >;
}

interface LogInContext {
  username: InputState<string>;
  setUsername: React.Dispatch<React.SetStateAction<LogInContext['username']>>;
  password: InputState<string>;
  setPassword: React.Dispatch<React.SetStateAction<LogInContext['password']>>;
  staySignedIn: InputState<boolean>;
  setStaySignedIn: React.Dispatch<
    React.SetStateAction<LogInContext['staySignedIn']>
  >;
  valid: boolean;
  setValid: React.Dispatch<React.SetStateAction<LogInContext['valid']>>;
  loading: boolean;
  setLoading: React.Dispatch<React.SetStateAction<LogInContext['loading']>>;
  error: string | null;
  setError: React.Dispatch<React.SetStateAction<LogInContext['error']>>;
}

interface LogInWithEmailContext {
  email: InputState<string>;
  setEmail: React.Dispatch<
    React.SetStateAction<LogInWithEmailContext['email']>
  >;
  screen: 'email' | 'sent';
  setScreen: React.Dispatch<
    React.SetStateAction<LogInWithEmailContext['screen']>
  >;
  valid: boolean;
  setValid: React.Dispatch<
    React.SetStateAction<LogInWithEmailContext['valid']>
  >;
  loading: boolean;
  setLoading: React.Dispatch<
    React.SetStateAction<LogInWithEmailContext['loading']>
  >;
}

interface SignUpContext {
  email: InputState<string>;
  setEmail: React.Dispatch<React.SetStateAction<SignUpContext['email']>>;
  password: InputState<string>;
  setPassword: React.Dispatch<React.SetStateAction<SignUpContext['password']>>;
  confirmPassword: InputState<string>;
  setConfirmPassword: React.Dispatch<
    React.SetStateAction<SignUpContext['confirmPassword']>
  >;
  valid: boolean;
  setValid: React.Dispatch<React.SetStateAction<SignUpContext['valid']>>;
  error: string | null;
  setError: React.Dispatch<React.SetStateAction<SignUpContext['error']>>;
  loading: boolean;
  setLoading: React.Dispatch<React.SetStateAction<SignUpContext['loading']>>;
}

interface Modal {
  component: React.ReactNode;
  contentStyle: React.CSSProperties;
  includeExitButton: boolean;
  onExit: () => void;
  key: string;
}

const defaultModal: Modal = {
  component: null,
  onExit: () => null,
  includeExitButton: true,
  contentStyle: {},
  key: null,
};

interface GlobalModalsContext {
  activeModal: Modal | null;
  setModal: (modal: Partial<Modal>) => void;
}

interface DeviceContext {
  isMobile: boolean;
}

interface Reducer<State, Dispatch> {
  state: State;
  dispatch: (action: Dispatch) => void;
}

interface DataContext {
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

interface ToastContext {
  state: ToastContextState;
  dispatch: React.Dispatch<ToastReducerAction>;
  make: (toast: Toast) => ToastId;
  makePending: (toast: ToastNoType) => ToastId;
  update: (id: ToastId, toast: Partial<Toast>) => void;
}

type AuthContextState = components['schemas']['GetAuthBaseReturn'];

interface AuthContext {
  state: AuthContextState;
  setState: React.Dispatch<React.SetStateAction<AuthContextState>>;
  logOut: () => void;
  updateFromApiResponse: (data: any) => void;
}

interface EscapeKeyContext {
  addCallback: (callback: () => void) => void;
  removeCallback: (callback: () => void) => void;
}

interface ConfirmationModal {
  title: string;
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
  confirmText?: string;
  cancelText?: string;
}

interface SurfaceContextValue {
  level: number;
  mode: 'a' | 'b';
}

export {
  ExtractResponseTypes,
  CallApiProps,
  CallApiReturn,
  UseApiCallReturn,
  DarkModeContext,
  defaultInputState,
  InputState,
  InputValue,
  InputStatus,
  SignUpContext,
  LogInContext,
  LogInWithEmailContext,
  Toast,
  ToastId,
  ToastNoType,
  ToastContextState,
  ToastReducerActionTypes,
  ToastReducerAction,
  ToastContext,
  AuthContextState,
  AuthContext,
  DeviceContext,
  Modal,
  defaultModal,
  GlobalModalsContext,
  AuthModalsContext,
  AuthModalsType,
  DataContext,
  EscapeKeyContext,
  ConfirmationModal,
  SurfaceContextValue,
};
