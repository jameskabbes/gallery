import React, { useEffect, useState, useReducer, createContext } from 'react';
import { AuthContextState, AuthContext as AuthContextType } from '../types';
import { paths, operations, components } from '../openapi_schema';
import config from '../../../config.json';

const defaultState: AuthContextState = {
  loggedIn: false,
  user: null,
  token: null,
};

const statusCodesToLogOut = new Set([401, 403]);

const AuthContext = createContext<AuthContextType>({
  state: null,
  setState: () => {},
  logOut: () => {},
  updateFromApiResponse: (data: any, status_code: number) => {},
});

interface Props {
  children: React.ReactNode;
}

function AuthContextProvider({ children }: Props) {
  const [state, setState] = useState<AuthContextState>(defaultState);

  function logOut() {
    setState(defaultState);
  }

  function updateFromApiResponse(data: any, status_code: number) {
    if (statusCodesToLogOut.has(status_code)) {
      return logOut();
    } else if (data && config.auth_key in data) {
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
