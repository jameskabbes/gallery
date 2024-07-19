import React, { useReducer, createContext } from 'react';
import {
  ConfirmationModalContext as ConfirmationModalContextType,
  ConfirmationModalContextAction,
  ConfirmationModalContextState,
} from '../types';

const defaultStateValue: ConfirmationModalContextState = {
  isActive: false,
  isConfirmed: null,
  title: null,
  message: null,
};

function confirmationModalReducer(
  state: ConfirmationModalContextState,
  action: ConfirmationModalContextAction
): ConfirmationModalContextState {
  switch (action.type) {
    case 'SET_IS_ACTIVE':
      return { ...state, isActive: action.payload };
    case 'CONFIRM':
      return { ...state, isConfirmed: true, isActive: false };
    case 'CANCEL':
      return { ...state, isConfirmed: false, isActive: false };
    case 'RESET':
      return { ...defaultStateValue };
    case 'SET_TITLE':
      return { ...state, title: action.payload };
    case 'SET_MESSAGE':
      return { ...state, message: action.payload };
    default:
      return state;
  }
}

const ConfirmationModalContext = createContext<ConfirmationModalContextType>({
  state: defaultStateValue,
  dispatch: () => null,
});

interface Props {
  children: React.ReactNode;
}

function ConfirmationModalContextProvider({ children }: Props) {
  const [state, dispatch] = useReducer(
    confirmationModalReducer,
    defaultStateValue
  );

  return (
    <ConfirmationModalContext.Provider
      value={{
        state,
        dispatch,
      }}
    >
      {children}
    </ConfirmationModalContext.Provider>
  );
}

export { ConfirmationModalContext, ConfirmationModalContextProvider };
