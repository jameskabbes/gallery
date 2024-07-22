import React, { useReducer, createContext, useEffect } from 'react';
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
  showModal: () => false,
});

interface Props {
  children: React.ReactNode;
}

function ConfirmationModalContextProvider({ children }: Props) {
  const [state, dispatch] = useReducer(
    confirmationModalReducer,
    defaultStateValue
  );
  const [resolve, setResolve] = React.useState<
    ((value: boolean | PromiseLike<boolean>) => void) | null
  >();

  function showModal(title: string, message: string): Promise<boolean> {
    dispatch({ type: 'SET_TITLE', payload: title });
    dispatch({ type: 'SET_MESSAGE', payload: message });
    dispatch({ type: 'SET_IS_ACTIVE', payload: true });
    return new Promise((resolve) => {
      setResolve(() => resolve);
    });
  }

  useEffect(() => {
    if (state.isConfirmed !== null) {
      resolve?.(state.isConfirmed);
      dispatch({ type: 'RESET' });
    }
  }, [state.isConfirmed]);

  return (
    <ConfirmationModalContext.Provider
      value={{
        state,
        dispatch,
        showModal,
      }}
    >
      {children}
    </ConfirmationModalContext.Provider>
  );
}

export { ConfirmationModalContext, ConfirmationModalContextProvider };
