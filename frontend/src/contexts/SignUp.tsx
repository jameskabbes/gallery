import React, { useEffect, useState, useReducer, createContext } from 'react';
import {
  SignUpContext as SignUpContextType,
  defaultInputState,
} from '../types';

const SignUpContext = createContext<SignUpContextType>({
  email: null,
  setEmail: () => {},
  password: null,
  setPassword: () => {},
  confirmPassword: null,
  setConfirmPassword: () => {},
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
    ...defaultInputState<SignUpContextType['email']['value']>(''),
  });
  const [password, setPassword] = useState<SignUpContextType['password']>({
    ...defaultInputState<SignUpContextType['password']['value']>(''),
  });
  const [confirmPassword, setConfirmPassword] = useState<
    SignUpContextType['confirmPassword']
  >({
    ...defaultInputState<SignUpContextType['confirmPassword']['value']>(''),
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
