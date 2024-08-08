import React, { useReducer, createContext } from 'react';
import {
  ModalContext as ModalContextType,
  ModalReducerState,
  ModalReducerAction,
} from '../types';

import { Modal } from '../components/Modal';

function modalReducer(
  state: ModalReducerState,
  action: ModalReducerAction
): ModalReducerState {
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

const modalReducerDefaultState: ModalReducerState = {
  stack: [],
};

const ModalContext = createContext<ModalContextType>({
  state: null,
  dispatch: () => null,
});

interface Props {
  children: React.ReactNode;
}

function ModalContextProvider({ children }: Props) {
  const [state, dispatch] = useReducer(modalReducer, modalReducerDefaultState);

  return (
    <ModalContext.Provider
      value={{
        state,
        dispatch,
      }}
    >
      {children}
    </ModalContext.Provider>
  );
}

export { ModalContext, ModalContextProvider };
