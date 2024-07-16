import React, { useState, useEffect, createContext } from 'react';
import { ToastContext as ToastContextType } from '../types';

const defaultContextValue: ToastContextType = {
  toasts: [],
};

const ToastContext = createContext<ToastContextType>({
  ...defaultContextValue,
});

interface Props {
  children: React.ReactNode;
}

function ToastContextProvider({ children }: Props) {
  const [toasts, setToasts] = useState<ToastContextType['toasts']>(
    defaultContextValue.toasts
  );

  return (
    <ToastContext.Provider
      value={{
        toasts,
      }}
    >
      {children}
    </ToastContext.Provider>
  );
}

export { ToastContext, ToastContextProvider };
