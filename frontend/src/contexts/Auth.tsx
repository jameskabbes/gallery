import React, { useEffect, useState, useReducer, createContext } from 'react';
import { AuthContextState, AuthContext as AuthContextType } from '../types';
import { paths, operations, components } from '../openapi_schema';
import config from '../../../config.json';
import { callApi } from '../utils/Api';

const defaultState: AuthContextState = {
  user: null,
  scopes: [],
  expiry: null,
};

const AuthContext = createContext<AuthContextType>({
  state: null,
  setState: () => {},
  logOut: () => {},
  updateFromApiResponse: (data: any) => {},
});

interface Props {
  children: React.ReactNode;
}

function AuthContextProvider({ children }: Props) {
  const [state, setState] = useState<AuthContextState>(defaultState);

  useEffect(() => {
    localStorage.setItem(config.auth_key, JSON.stringify(state));
  }, [state]);

  useEffect(() => {
    function handleStorageEvent(event: StorageEvent) {
      if (event.key === config.auth_key) {
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

  function logOut() {
    setState(defaultState);
  }

  function updateFromApiResponse(data: any) {
    if (data && config.auth_key in data) {
      return setState(data[config.auth_key]);
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
