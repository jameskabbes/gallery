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
  username: InputState;
  password: InputState;
  valid: boolean;
}

type LogInReducerAction =
  | {
      type: 'SET_VALID';
      payload: LogInContextState['valid'];
    }
  | {
      type: 'SET_USERNAME';
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

interface SignUpContextState {
  isActive: boolean;
  username: InputState;
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
      type: 'SET_USERNAME';
      payload: InputState;
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

type GlobalModalsType = 'logIn' | 'signUp';

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
