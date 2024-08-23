import React, { useEffect, useState, useReducer, createContext } from 'react';
import {
  AuthContextAction,
  AuthContextState,
  AuthContext as AuthContextType,
} from '../types';

import siteConfig from '../../siteConfig.json';

function removeToken() {
  localStorage.removeItem(siteConfig['access_token_key']);
}

function authReducer(
  state: AuthContextState,
  action: AuthContextAction
): AuthContextState {
  switch (action.type) {
    case 'SET_TOKEN':
      localStorage.setItem(
        siteConfig['access_token_key'],
        action.payload.access_token
      );
      var newState = { ...state, token: action.payload.access_token };
      return newState;

    case 'LOGIN':
      var newState = {
        ...state,
        auth: action.payload,
        isActive: true,
      };
      return newState;
    case 'LOGOUT':
      removeToken();
      return {
        isActive: false,
        auth: null,
        token: null,
      };
    case 'UPDATE':
      let exception = action.payload.exception;
      if (exception) {
        if (
          exception === 'credentials' ||
          exception === 'invalid_token' ||
          exception === 'token_expired' ||
          exception === 'user_not_found' ||
          exception === 'missing_required_claims'
        ) {
          removeToken();
          return {
            auth: null,
            token: null,
            isActive: false,
          };
        }
      } else {
        return {
          ...state,
          auth: action.payload,
          isActive: true,
        };
      }

    default:
      return state;
  }
}

const authReducerDefaultState: AuthContextState = {
  auth: null,
  token: null,
  isActive: false,
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
