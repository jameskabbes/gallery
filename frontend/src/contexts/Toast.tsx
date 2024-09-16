import React, { useEffect, useState, useReducer, createContext } from 'react';
import {
  Toast,
  ToastId,
  ToastNoType,
  ToastContext as ToastContextType,
  ToastContextState,
  ToastReducerAction,
} from '../types';

const toastReducerDefaultState: ToastContextState = {
  toasts: new Map<string, Toast>([
    ['1', { type: 'info', message: 'Welcome to the gallery!' }],
  ]),
};

function toastReducer(state: ToastContextState, action: ToastReducerAction) {
  switch (action.type) {
    case 'ADD':
      return {
        ...state,
        toasts: new Map([
          ...state.toasts,
          [action.payload.id, action.payload.toast],
        ]),
      };
    case 'REMOVE':
      state.toasts.delete(action.payload);
      return { ...state, toasts: new Map([...state.toasts]) };
    case 'UPDATE':
      const newToast = state.toasts.get(action.payload.id);
      if (!newToast) {
        return state;
      }
      // update the toast with action.payload.toast
      state.toasts.set(action.payload.id, {
        ...newToast,
        ...action.payload.toast,
      });
      return { ...state, toasts: new Map([...state.toasts]) };
    case 'CLEAR':
      return { ...toastReducerDefaultState };
    default:
      return state;
  }
}

const ToastContext = createContext<ToastContextType>({
  state: toastReducerDefaultState,
  dispatch: () => {},
  make: () => '',
  makePending: () => '',
  update: () => {},
});

interface Props {
  children: React.ReactNode;
}

function ToastContextProvider({ children }: Props) {
  const [state, dispatch] = useReducer(toastReducer, toastReducerDefaultState);

  function make(toast: Toast): ToastId {
    const id = Math.random().toString(12);
    dispatch({ type: 'ADD', payload: { id, toast } });
    return id;
  }
  function makePending(toast: ToastNoType): ToastId {
    return make({ ...toast, type: 'pending' });
  }

  function update(id: ToastId, toast: Partial<Toast>) {
    dispatch({ type: 'UPDATE', payload: { id, toast } });
  }

  return (
    <ToastContext.Provider
      value={{ state, dispatch, make, makePending, update }}
    >
      {children}
    </ToastContext.Provider>
  );
}

export { ToastContext, ToastContextProvider };
