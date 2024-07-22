import React, { useState, useEffect, createContext, useReducer } from 'react';
import {
  ToastContext as ToastContextType,
  ToastContextAction,
  ToastContextAddToast,
  ToastContextState,
  ToastType,
  Toast,
} from '../types';

const defaultContextValue: ToastContextState = {
  toasts: new Map(),
};

function toastReducer(
  state: ToastContextState,
  action: ToastContextAction
): ToastContextState {
  switch (action.type) {
    case 'ADD':
      var newState = {
        ...state,
        toasts: new Map(state.toasts),
      };
      newState.toasts.set(action.payload.id, action.payload);
      return newState;
    case 'DELETE':
      var newState = {
        ...state,
        toasts: new Map(state.toasts),
      };
      newState.toasts.delete(action.payload);
      return newState;
    case 'CLEAR':
      return defaultContextValue;
    default:
      return state;
  }
}

const ToastContext = createContext<ToastContextType>({
  state: defaultContextValue,
  dispatch: () => null,
  addToast: () => null,
});

interface Props {
  children: React.ReactNode;
}

function ToastContextProvider({ children }: Props) {
  const [state, dispatch] = useReducer(toastReducer, defaultContextValue);
  function addToast(toast: Omit<Toast, 'id'>) {
    const id = Math.random();
    let newToast: Toast = { ...toast, id };
    dispatch({ type: 'ADD', payload: newToast });

    setTimeout(() => {
      dispatch({ type: 'DELETE', payload: id });
    }, 3000);
  }

  return (
    <ToastContext.Provider
      value={{
        state,
        dispatch,
        addToast,
      }}
    >
      {children}
    </ToastContext.Provider>
  );
}

export { ToastContext, ToastContextProvider };
