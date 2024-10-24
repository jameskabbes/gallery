import React, { useEffect, useState, useReducer, createContext } from 'react';
import {
  SignUpContext as SignUpContextType,
  defaultValidatedInputState,
} from '../types';

const SignUpContext = createContext<SignUpContextType>({
  email: null,
  setEmail: () => {},
  password: null,
  setPassword: () => {},
  confirmPassword: null,
  setConfirmPassword: () => {},
  staySignedIn: null,
  setStaySignedIn: () => {},
  valid: false,
  setValid: () => {},
  loading: false,
  setLoading: () => {},
  error: null,
  setError: () => {},
});

interface Props {
  children: React.ReactNode;
}

function SignUpContextProvider({ children }: Props) {
  const [email, setEmail] = useState<SignUpContextType['email']>({
    ...defaultValidatedInputState<SignUpContextType['email']['value']>(''),
  });
  const [password, setPassword] = useState<SignUpContextType['password']>({
    ...defaultValidatedInputState<SignUpContextType['password']['value']>(''),
  });
  const [confirmPassword, setConfirmPassword] = useState<
    SignUpContextType['confirmPassword']
  >({
    ...defaultValidatedInputState<
      SignUpContextType['confirmPassword']['value']
    >(''),
  });
  const [staySignedIn, setStaySignedIn] = useState<
    SignUpContextType['staySignedIn']
  >({
    ...defaultValidatedInputState<SignUpContextType['staySignedIn']['value']>(
      false
    ),
  });

  const [valid, setValid] = useState<SignUpContextType['valid']>(false);
  const [loading, setLoading] = useState<SignUpContextType['loading']>(false);
  const [error, setError] = useState<SignUpContextType['error']>(null);

  return (
    <SignUpContext.Provider
      value={{
        email,
        setEmail,
        password,
        setPassword,
        confirmPassword,
        setConfirmPassword,
        staySignedIn,
        setStaySignedIn,
        valid,
        setValid,
        loading,
        setLoading,
        error,
        setError,
      }}
    >
      {children}
    </SignUpContext.Provider>
  );
}

export { SignUpContext, SignUpContextProvider };
