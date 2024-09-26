import React, { useEffect, useState, useReducer, createContext } from 'react';
import {
  SignUpContext as SignUpContextType,
  SignUpContextState,
  SignUpReducerAction,
  defaultInputState,
} from '../types';

const signUpReducerDefaultState: SignUpContextState = {
  active: false,
  email: { ...defaultInputState },
  password: { ...defaultInputState },
  confirmPassword: { ...defaultInputState },
  valid: false,
};

function signUpReducer(state: SignUpContextState, action: SignUpReducerAction) {
  switch (action.type) {
    case 'SET_VALID':
      return { ...state, valid: action.payload };
    case 'SET_EMAIL':
      return { ...state, email: action.payload };
    case 'SET_PASSWORD':
      return { ...state, password: action.payload };
    case 'SET_CONFIRM_PASSWORD':
      return { ...state, confirmPassword: action.payload };
    case 'SET_ACTIVE':
      return { ...state, active: action.payload };
    case 'RESET':
      return { ...signUpReducerDefaultState };
    default:
      return state;
  }
}

const SignUpContext = createContext<SignUpContextType>({
  state: signUpReducerDefaultState,
  dispatch: () => {},
});

interface Props {
  children: React.ReactNode;
}

function SignUpContextProvider({ children }: Props) {
  const [state, dispatch] = useReducer(
    signUpReducer,
    signUpReducerDefaultState
  );

  return (
    <SignUpContext.Provider value={{ state, dispatch }}>
      {children}
    </SignUpContext.Provider>
  );
}

export { SignUpContext, SignUpContextProvider };
