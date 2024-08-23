import React, { useEffect, useState, useReducer, createContext } from 'react';
import {
  LoginContext as LoginContextType,
  LoginContextState,
  LoginContextAction,
  defaultInputState,
} from '../types';

function loginReducer(state: LoginContextState, action: LoginContextAction) {
  switch (action.type) {
    case 'SET_VALID':
      return { ...state, valid: action.payload };
    case 'SET_USERNAME':
      return { ...state, username: action.payload };
    case 'SET_PASSWORD':
      return { ...state, password: action.payload };
    case 'SET_ACTIVE':
      return { ...state, isActive: action.payload };
    default:
      return state;
  }
}

const loginReducerDefaultState: LoginContextState = {
  isActive: false,
  username: defaultInputState,
  password: defaultInputState,
  valid: false,
};

const LoginContext = createContext<LoginContextType>({
  state: null,
  dispatch: () => {},
});

interface Props {
  children: React.ReactNode;
}

function LoginContextProvider({ children }: Props) {
  const [state, dispatch] = useReducer(loginReducer, loginReducerDefaultState);

  return (
    <LoginContext.Provider value={{ state, dispatch }}>
      {children}
    </LoginContext.Provider>
  );
}

export { LoginContext, LoginContextProvider };
