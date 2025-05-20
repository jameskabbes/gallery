import React, { useEffect, useState, useReducer, createContext } from 'react';
import {
  ToastType,
  ToastId,
  ToastNoType,
  ToastContextType,
  ToastContextState,
  ToastReducerAction,
} from '../types';

const toastReducerDefaultState: ToastContextState = {
  toasts: new Map<string, ToastType>(),
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

export const ToastContext = createContext<ToastContextType>({
  state: toastReducerDefaultState,
  dispatch: () => {},
  make: () => '',
  makePending: () => '',
  update: () => {},
});

export function ToastContextProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [state, dispatch] = useReducer(toastReducer, toastReducerDefaultState);

  function make(toast: ToastType): ToastId {
    const id = Math.random().toString(12);
    dispatch({ type: 'ADD', payload: { id, toast } });
    return id;
  }
  function makePending(toast: ToastNoType): ToastId {
    return make({ ...toast, type: 'pending' });
  }

  function update(id: ToastId, toast: Partial<ToastType>) {
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
