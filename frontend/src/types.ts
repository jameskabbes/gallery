import { paths, operations, components } from './openapi_schema';

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

interface DeviceContext {
  isMobile: boolean;
}

interface AuthContext {
  token: string | null;
  user: string | null;
}

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
