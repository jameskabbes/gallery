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

type Input = string | number | readonly string[];

interface InputState<T extends Input> {
  value: T;
  status: InputStatus;
  error: string | null;
}

const defaultInputState = <T extends Input>(
  defaultValue: T
): InputState<T> => ({
  value: defaultValue,
  status: 'valid',
  error: null,
});

interface DarkModeContext {
  state: boolean;
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

interface AuthModalsContextStateBase {
  valid: boolean;
}

type AuthModalsReducerActionBase =
  | { type: 'RESET' }
  | { type: 'SET_VALID'; payload: boolean };

interface LogInContextState extends AuthModalsContextStateBase {
  email: InputState<string>;
  password: InputState<string>;
}

type LogInReducerAction =
  | {
      type: 'SET_EMAIL';
      payload: LogInContextState['email'];
    }
  | {
      type: 'SET_PASSWORD';
      payload: LogInContextState['password'];
    }
  | AuthModalsReducerActionBase;

interface LogInContext {
  state: LogInContextState;
  dispatch: React.Dispatch<LogInReducerAction>;
}

interface LogInWithEmailContextState extends AuthModalsContextStateBase {
  email: InputState<string>;
  screen: 'email' | 'sent';
}

type LogInWithEmailReducerAction =
  | {
      type: 'SET_EMAIL';
      payload: LogInWithEmailContextState['email'];
    }
  | {
      type: 'SET_SCREEN';
      payload: LogInWithEmailContextState['screen'];
    }
  | AuthModalsReducerActionBase;

interface LogInWithEmailContext {
  state: LogInWithEmailContextState;
  dispatch: React.Dispatch<LogInWithEmailReducerAction>;
}

interface SignUpContextState extends AuthModalsContextStateBase {
  email: InputState<string>;
  password: InputState<string>;
  confirmPassword: InputState<string>;
}

type SignUpReducerAction =
  | {
      type: 'SET_EMAIL';
      payload: SignUpContextState['email'];
    }
  | {
      type: 'SET_PASSWORD';
      payload: SignUpContextState['password'];
    }
  | {
      type: 'SET_CONFIRM_PASSWORD';
      payload: SignUpContextState['confirmPassword'];
    }
  | AuthModalsReducerActionBase;

interface SignUpContext {
  state: SignUpContextState;
  dispatch: React.Dispatch<SignUpReducerAction>;
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

export {
  ExtractResponseTypes,
  CallApiProps,
  CallApiReturn,
  UseApiCallReturn,
  DarkModeContext,
  defaultInputState,
  Input,
  InputState,
  InputStatus,
  SignUpContextState,
  SignUpReducerAction,
  SignUpContext,
  LogInContextState,
  LogInReducerAction,
  LogInContext,
  LogInWithEmailContextState,
  LogInWithEmailReducerAction,
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
};
