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

interface ConfirmationModalContextState {
  isActive: boolean;
  isConfirmed: boolean | null;
  title: string | null;
  message: string | null;
}

type ConfirmationModalContextAction =
  | { type: 'SET_IS_ACTIVE'; payload: boolean }
  | { type: 'CONFIRM' }
  | { type: 'CANCEL' }
  | { type: 'RESET' }
  | { type: 'SET_TITLE'; payload: string }
  | { type: 'SET_MESSAGE'; payload: string };

type ConfirmationModalContextShowModal = (
  title: string,
  message: string
) => boolean | PromiseLike<boolean>;

interface ConfirmationModalContext {
  state: ConfirmationModalContextState;
  dispatch: React.Dispatch<ConfirmationModalContextAction>;
  showModal: ConfirmationModalContextShowModal;
}

//
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

export {
  ExtractResponseTypes,
  DarkModeContext,
  ConfirmationModalContextState,
  ConfirmationModalContextAction,
  ConfirmationModalContext,
  ConfirmationModalContextShowModal,
  StudiosReducerState,
  StudiosReducerAction,
  DataContext,
  Studios,
};
