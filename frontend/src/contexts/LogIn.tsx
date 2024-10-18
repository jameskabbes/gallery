import React, { useEffect, useState, useReducer, createContext } from 'react';
import {
  LogInContext as LogInContextType,
  defaultInputState,
  InputState,
} from '../types';

const LogInContext = createContext<LogInContextType>({
  username: null,
  setUsername: () => {},
  password: null,
  setPassword: () => {},
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

function LogInContextProvider({ children }: Props) {
  const [username, setUsername] = useState<LogInContextType['username']>({
    ...defaultInputState<LogInContextType['username']['value']>(''),
  });
  const [password, setPassword] = useState<LogInContextType['password']>({
    ...defaultInputState<LogInContextType['username']['value']>(''),
  });
  const [staySignedIn, setStaySignedIn] = useState<
    LogInContextType['staySignedIn']
  >({
    ...defaultInputState<LogInContextType['staySignedIn']['value']>(false),
  });
  const [valid, setValid] = useState<LogInContextType['valid']>(false);
  const [loading, setLoading] = useState<LogInContextType['loading']>(false);
  const [error, setError] = useState<LogInContextType['error']>(null);

  return (
    <LogInContext.Provider
      value={{
        username,
        setUsername,
        password,
        setPassword,
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
    </LogInContext.Provider>
  );
}

export { LogInContext, LogInContextProvider };
