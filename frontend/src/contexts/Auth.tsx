import React, { useEffect, useState, useReducer, createContext } from 'react';
import {
  AuthReducerAction,
  AuthContextState,
  AuthContext as AuthContextType,
  AuthReducerActionTypes,
} from '../types';

import { paths, operations, components } from '../openapi_schema';
import siteConfig from '../../siteConfig.json';
import config from '../../../config.json';

const cancellableExceptions = new Set<string>([
  'credentials',
  'invalid_token',
  'token_expired',
  'user_not_found',
  'missing_required_claims',
]);

function clearTokenStorage() {
  localStorage.removeItem(siteConfig['access_token_key']);
}

function setTokenStorage(token: AuthContextState['token']) {
  localStorage.setItem(siteConfig['access_token_key'], token);
}

function setToken(
  state: AuthContextState,
  payload: AuthReducerActionTypes['SET_TOKEN']['payload']
): AuthContextState {
  setTokenStorage(payload.access_token);
  return { ...state, token: payload.access_token };
}

function clearToken(state: AuthContextState): AuthContextState {
  clearTokenStorage();
  return {
    ...state,
    token: null,
  };
}

function logout(): AuthContextState {
  clearTokenStorage();
  return {
    auth: null,
    token: null,
  };
}

function login(
  state: AuthContextState,
  payload: AuthReducerActionTypes['LOGIN']['payload']
): AuthContextState {
  return {
    ...state,
    auth: payload,
  };
}

function setAuthUser(
  state: AuthContextState,
  payload: AuthReducerActionTypes['SET_AUTH_USER']['payload']
): AuthContextState {
  if (state.auth) {
    return {
      ...state,
      auth: { ...state.auth, user: payload },
    };
  } else {
    return state;
  }
}

function update(
  state: AuthContextState,
  payload: AuthReducerActionTypes['UPDATE']['payload']
): AuthContextState {
  let exception = payload.exception;
  if (cancellableExceptions.has(exception)) {
    return logout();
  } else {
    return login(state, payload);
  }
}

function updateFromApiResponse(
  state: AuthContextState,
  payload: AuthReducerActionTypes['UPDATE_FROM_API_RESPONSE']['payload']
): AuthContextState {
  if (payload && config.auth_key in payload) {
    return update(state, payload[config.auth_key]);
  } else {
    return state;
  }
}

function authReducer(
  state: AuthContextState,
  action: AuthReducerAction
): AuthContextState {
  switch (action.type) {
    case 'SET_AUTH_USER':
      return setAuthUser(state, action.payload);
    case 'SET_TOKEN':
      return setToken(state, action.payload);
    case 'CLEAR_TOKEN':
      return clearToken(state);
    case 'LOGIN':
      return login(state, action.payload);
    case 'LOGOUT':
      return logout();
    case 'UPDATE':
      return update(state, action.payload);
    case 'UPDATE_FROM_API_RESPONSE':
      return updateFromApiResponse(state, action.payload);
    default:
      return state;
  }
}

const authReducerDefaultState: AuthContextState = {
  auth: null,
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

  // Add this function to handle the storage event
  function handleStorageEvent(event: StorageEvent) {
    if (event.key === siteConfig['access_token_key']) {
      // Dispatch an action to update the state based on the new token value
      if (event.newValue) {
        dispatch({
          type: 'SET_TOKEN',
          payload: { access_token: event.newValue },
        });
      } else {
        dispatch({ type: 'LOGOUT' });
      }
    }
  }

  useEffect(() => {
    window.addEventListener('storage', handleStorageEvent);

    return () => {
      window.removeEventListener('storage', handleStorageEvent);
    };
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
