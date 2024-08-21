import { paths, operations, components } from './openapi_schema';

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
  user: components['schemas']['UserPublic'] | null;
  token: string | null;
}

type AuthContextAction =
  | {
      type: 'LOGIN';
      payload: {
        user: components['schemas']['UserPublic'];
        token: string;
      };
    }
  | { type: 'LOGOUT' };

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
