import React, { useEffect, useState, useReducer, createContext } from 'react';
import {
  LogInWithEmailContext as LogInWithEmailContextType,
  LogInWithEmailReducerAction,
  LogInWithEmailContextState,
  defaultInputState,
} from '../types';

const logInWithEmailReducerDefaultState: LogInWithEmailContextState = {
  isActive: false,
  email: { ...defaultInputState },
  valid: false,
  screen: 'email',
};

function logInWithEmailReducer(
  state: LogInWithEmailContextState,
  action: LogInWithEmailReducerAction
) {
  switch (action.type) {
    case 'SET_VALID':
      return { ...state, valid: action.payload };
    case 'SET_EMAIL':
      return { ...state, email: action.payload };
    case 'SET_ACTIVE':
      if (action.payload === true) {
        return {
          ...state,
          isActive: action.payload,
          screen: logInWithEmailReducerDefaultState.screen,
        };
      }
      return { ...state, isActive: action.payload };
    case 'SET_SCREEN':
      return { ...state, screen: action.payload };
    case 'RESET':
      return { ...logInWithEmailReducerDefaultState };
    default:
      return state;
  }
}

const LogInWithEmailContext = createContext<LogInWithEmailContextType>({
  state: logInWithEmailReducerDefaultState,
  dispatch: () => {},
});

interface Props {
  children: React.ReactNode;
}

function LogInWithEmailContextProvider({ children }: Props) {
  const [state, dispatch] = useReducer(
    logInWithEmailReducer,
    logInWithEmailReducerDefaultState
  );

  return (
    <LogInWithEmailContext.Provider value={{ state, dispatch }}>
      {children}
    </LogInWithEmailContext.Provider>
  );
}

export { LogInWithEmailContext, LogInWithEmailContextProvider };
