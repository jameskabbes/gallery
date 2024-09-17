import { paths, operations, components } from './openapi_schema';
import config from '../../config.json';

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

interface InputState {
  value: string;
  status: InputStatus;
  error: string | null;
}

const defaultInputState: InputState = {
  value: '',
  status: 'valid',
  error: null,
};

interface DarkModeContext {
  state: boolean;
  toggle: () => void;
}

interface LogInContextState {
  isActive: boolean;
  email: InputState;
  password: InputState;
  valid: boolean;
}

type LogInReducerAction =
  | {
      type: 'SET_VALID';
      payload: LogInContextState['valid'];
    }
  | {
      type: 'SET_EMAIL';
      payload: InputState;
    }
  | {
      type: 'SET_PASSWORD';
      payload: InputState;
    }
  | {
      type: 'SET_ACTIVE';
      payload: LogInContextState['isActive'];
    }
  | { type: 'RESET' };

interface LogInContext {
  state: LogInContextState;
  dispatch: React.Dispatch<LogInReducerAction>;
}

interface LogInWithEmailContextState {
  isActive: boolean;
  email: InputState;
  valid: boolean;
}

type LogInWithEmailReducerAction =
  | {
      type: 'SET_VALID';
      payload: LogInWithEmailContextState['valid'];
    }
  | {
      type: 'SET_EMAIL';
      payload: InputState;
    }
  | {
      type: 'SET_ACTIVE';
      payload: LogInWithEmailContextState['isActive'];
    }
  | { type: 'RESET' };

interface LogInWithEmailContext {
  state: LogInWithEmailContextState;
  dispatch: React.Dispatch<LogInWithEmailReducerAction>;
}

interface SignUpContextState {
  isActive: boolean;
  email: InputState;
  password: InputState;
  confirmPassword: InputState;
  valid: boolean;
}

type SignUpReducerAction =
  | {
      type: 'SET_VALID';
      payload: LogInContextState['valid'];
    }
  | {
      type: 'SET_EMAIL';
      payload: InputState;
    }
  | {
      type: 'SET_PASSWORD';
      payload: InputState;
    }
  | {
      type: 'SET_CONFIRM_PASSWORD';
      payload: InputState;
    }
  | {
      type: 'SET_ACTIVE';
      payload: LogInContextState['isActive'];
    }
  | { type: 'RESET' };

interface SignUpContext {
  state: SignUpContextState;
  dispatch: React.Dispatch<SignUpReducerAction>;
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

interface AuthContextState {
  isActive: boolean;
  auth: components['schemas']['GetAuthReturn'];
  token: components['schemas']['Token']['access_token'] | null;
}

interface AuthReducerActionTypes {
  SET_AUTH_USER: {
    type: 'SET_AUTH_USER';
    payload: AuthContextState['auth']['user'];
  };
  SET_TOKEN: {
    type: 'SET_TOKEN';
    payload: components['schemas']['Token'];
  };
  LOGIN: {
    type: 'LOGIN';
    payload: AuthContextState['auth'];
  };
  LOGOUT: {
    type: 'LOGOUT';
  };
  UPDATE: {
    type: 'UPDATE';
    payload: AuthContextState['auth'];
  };
  UPDATE_FROM_API_RESPONSE: {
    type: 'UPDATE_FROM_API_RESPONSE';
    payload: any;
  };
}

type AuthReducerAction = AuthReducerActionTypes[keyof AuthReducerActionTypes];

interface AuthContext {
  state: AuthContextState;
  dispatch: React.Dispatch<AuthReducerAction>;
}

type Modal = React.ReactNode;
interface ModalsReducerState {
  stack: Modal[];
}

type ModalsReducerAction = { type: 'PUSH'; payload: Modal } | { type: 'POP' };

interface ModalsContext {
  state: ModalsReducerState;
  dispatch: React.Dispatch<ModalsReducerAction>;
}

type GlobalModalsType = 'logIn' | 'signUp' | 'logInWithEmail';

interface GlobalModalsContext {
  toggleModal: (modal: GlobalModalsType) => void;
}

interface EscapeKeyContext {
  addCallback: (callback: () => void) => void;
  removeCallback: (callback: () => void) => void;
}

export {
  ExtractResponseTypes,
  CallApiProps,
  CallApiReturn,
  UseApiCallReturn,
  DarkModeContext,
  defaultInputState,
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
  AuthReducerActionTypes,
  AuthReducerAction,
  AuthContextState,
  AuthContext,
  DeviceContext,
  Modal,
  ModalsContext,
  ModalsReducerState,
  ModalsReducerAction,
  GlobalModalsType,
  GlobalModalsContext,
  DataContext,
  EscapeKeyContext,
};
