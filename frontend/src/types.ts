import { paths, operations, components } from './openapi_schema';
import config from '../../config.json';

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

interface LoginContextState {
  isActive: boolean;
  username: InputState;
  password: InputState;
  valid: boolean;
}

type LoginContextAction =
  | {
      type: 'SET_VALID';
      payload: LoginContextState['valid'];
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
      payload: LoginContextState['isActive'];
    };

interface LoginContext {
  state: LoginContextState;
  dispatch: React.Dispatch<LoginContextAction>;
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

type AuthContextAction =
  | {
      type: 'SET_TOKEN';
      payload: components['schemas']['Token'];
    }
  | {
      type: 'LOGIN';
      payload: AuthContextState['auth'];
    }
  | { type: 'LOGOUT' }
  | {
      type: 'UPDATE';
      payload: AuthContextState['auth'];
    };

interface AuthContext {
  state: AuthContextState;
  dispatch: React.Dispatch<AuthContextAction>;
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

export {
  ExtractResponseTypes,
  DarkModeContext,
  defaultInputState,
  InputState,
  InputStatus,
  LoginContextState,
  LoginContextAction,
  LoginContext,
  AuthContextAction,
  AuthContextState,
  AuthContext,
  DeviceContext,
  Modal,
  ModalsContext,
  ModalsReducerState,
  ModalsReducerAction,
  DataContext,
};
