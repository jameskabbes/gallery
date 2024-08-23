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

interface DarkModeContext {
  state: boolean;
  toggle: () => void;
}

interface DeviceContext {
  isMobile: boolean;
}

type Studios = Map<
  components['schemas']['StudioPublic']['id'],
  components['schemas']['StudioPublic']
>;

type StudiosReducerState = Studios;
type StudiosReducerAction =
  | { type: 'SET'; payload: Studios }
  | {
      type: 'ADD';
      payload: components['schemas']['StudioPublic'];
    }
  | { type: 'DELETE'; payload: components['schemas']['StudioPublic']['id'] };

interface Reducer<State, Dispatch> {
  state: State;
  dispatch: (action: Dispatch) => void;
}

interface DataContext {
  studios: Reducer<StudiosReducerState, StudiosReducerAction>;
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
  AuthContextAction,
  AuthContextState,
  AuthContext,
  DeviceContext,
  Modal,
  ModalsContext,
  ModalsReducerState,
  ModalsReducerAction,
  StudiosReducerState,
  StudiosReducerAction,
  DataContext,
  Studios,
};
