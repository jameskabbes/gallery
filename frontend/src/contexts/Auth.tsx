import React, { useEffect, useState, useReducer, createContext } from 'react';
import {
  AuthContextAction,
  AuthContextState,
  AuthContext as AuthContextType,
} from '../types';

import siteConfig from '../../siteConfig.json';

function authReducer(
  state: AuthContextState,
  action: AuthContextAction
): AuthContextState {
  switch (action.type) {
    case 'LOGIN':
      console.log('LOGIN', action.payload);
      return {
        ...state,
        token: action.payload.token,
        user: action.payload.user,
      };
    case 'LOGOUT':
      localStorage.removeItem(siteConfig['access_token_key']);
      return {
        ...state,
        token: null,
        user: null,
      };
    default:
      return state;
  }
}

const authReducerDefaultState: AuthContextState = {
  user: null,
  token: null,
};

const AuthContext = createContext<AuthContextType>({
  state: null,
  dispatch: () => null,
});

interface Props {
  children: React.ReactNode;
}

function AuthContextProvider({ children }: Props) {
  const [state, dispatch] = useReducer(authReducer, authReducerDefaultState);
  useEffect(() => {
    // Fetch the user's auth state
  }, []);

  return (
    <AuthContext.Provider
      value={{
        state,
        dispatch,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export { AuthContext, AuthContextProvider };
