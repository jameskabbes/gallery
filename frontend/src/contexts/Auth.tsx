import React, { useEffect, useState, useContext, createContext } from 'react';
import { AuthContextState, AuthContextType, ToastId } from '../types';
import { ToastContext } from './Toast';
import isEqual from 'lodash.isequal';
import { config } from '../config/config';

const defaultState: AuthContextState = {
  user: null,
  scope_ids: [],
  access_token: null,
};

export const AuthContext = createContext<AuthContextType>({
  state: { ...defaultState },
  setState: () => {},
  logOut: () => {},
  updateFromApiResponse: (data: any) => {},
});

export function AuthContextProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [state, setState] = useState<AuthContextState>(defaultState);
  const toastContext = useContext(ToastContext);

  useEffect(() => {
    localStorage.setItem(config.authKey, JSON.stringify(state));
  }, [state]);

  useEffect(() => {
    function handleStorageEvent(event: StorageEvent) {
      if (event.key === config.authKey) {
        const newValue = event.newValue
          ? JSON.parse(event.newValue)
          : defaultState;
        setState(newValue);
      }
    }

    window.addEventListener('storage', handleStorageEvent);
    return () => {
      window.removeEventListener('storage', handleStorageEvent);
    };
  }, []);

  function logOut(toastId?: ToastId) {
    setState(defaultState);

    if (toastId) {
      toastContext.update(toastId, {
        message: 'Logged out',
        type: 'info',
      });
    } else {
      toastContext.make({
        message: 'Logged out',
        type: 'info',
      });
    }
  }

  function updateFromApiResponse(data: any) {
    if (data && typeof data === 'object' && config.authKey in data) {
      // only update if the state is different
      if (!isEqual(data[config.authKey], state)) {
        return setState(data[config.authKey]);
      }
    }
  }

  return (
    <AuthContext.Provider
      value={{
        state,
        setState,
        logOut,
        updateFromApiResponse,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
