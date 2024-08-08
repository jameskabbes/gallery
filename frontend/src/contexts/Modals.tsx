import React, { useReducer, createContext } from 'react';
import {
  ModalsContext as ModalsContextType,
  ModalsReducerState,
  ModalsReducerAction,
} from '../types';

function modalsReducer(
  state: ModalsReducerState,
  action: ModalsReducerAction
): ModalsReducerState {
  switch (action.type) {
    case 'PUSH':
      return {
        stack: [...state.stack, action.payload],
      };
    case 'POP':
      return {
        stack: state.stack.slice(0, -1),
      };
    default:
      return state;
  }
}

const modalsReducerDefaultState: ModalsReducerState = {
  stack: [],
};

const ModalsContext = createContext<ModalsContextType>({
  state: null,
  dispatch: () => null,
});

interface Props {
  children: React.ReactNode;
}

function ModalsContextProvider({ children }: Props) {
  const [state, dispatch] = useReducer(
    modalsReducer,
    modalsReducerDefaultState
  );

  return (
    <ModalsContext.Provider
      value={{
        state,
        dispatch,
      }}
    >
      {children}
    </ModalsContext.Provider>
  );
}

export { ModalsContext, ModalsContextProvider };
