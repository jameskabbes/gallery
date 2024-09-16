import React, { useEffect, useState, useReducer, createContext } from 'react';
import {
  LogInContext as LogInContextType,
  LogInContextState,
  LogInReducerAction,
  defaultInputState,
} from '../types';

const logInReducerDefaultState: LogInContextState = {
  isActive: false,
  email: { ...defaultInputState },
  password: { ...defaultInputState },
  valid: false,
};

function logInReducer(state: LogInContextState, action: LogInReducerAction) {
  switch (action.type) {
    case 'SET_VALID':
      return { ...state, valid: action.payload };
    case 'SET_EMAIL':
      return { ...state, email: action.payload };
    case 'SET_PASSWORD':
      return { ...state, password: action.payload };
    case 'SET_ACTIVE':
      return { ...state, isActive: action.payload };
    case 'RESET':
      return { ...logInReducerDefaultState };
    default:
      return state;
  }
}

const LogInContext = createContext<LogInContextType>({
  state: logInReducerDefaultState,
  dispatch: () => {},
});

interface Props {
  children: React.ReactNode;
}

function LogInContextProvider({ children }: Props) {
  const [state, dispatch] = useReducer(logInReducer, logInReducerDefaultState);

  return (
    <LogInContext.Provider value={{ state, dispatch }}>
      {children}
    </LogInContext.Provider>
  );
}

export { LogInContext, LogInContextProvider };
