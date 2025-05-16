import React, { useEffect, useState, useContext, createContext } from 'react';
import { AuthContextState, AuthContextType, ToastId } from '../types';
import { paths, operations, components } from '../openapi_schema';
import { ToastContext } from './Toast';
import isEqual from 'lodash.isequal';
import { authKey } from '../../generateConfig';

const defaultState: AuthContextState = {
  user: null,
  scope_ids: [],
  auth_credential: null,
};

const AuthContext = createContext<AuthContextType>({
  state: { ...defaultState },
  setState: () => {},
  logOut: () => {},
  updateFromApiResponse: (data: any) => {},
});

function AuthContextProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthContextState>(defaultState);
  const toastContext = useContext(ToastContext);

  useEffect(() => {
    localStorage.setItem(authKey, JSON.stringify(state));
  }, [state]);

  useEffect(() => {
    function handleStorageEvent(event: StorageEvent) {
      if (event.key === authKey) {
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
    if (data && typeof data === 'object' && authKey in data) {
      // only update if the state is different
      if (!isEqual(data[authKey], state)) {
        return setState(data[authKey]);
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

export { AuthContext, AuthContextProvider };
