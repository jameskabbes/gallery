import React, { useEffect, useState, useReducer, createContext } from 'react';
import {
  LogInWithEmailContext as LogInWithEmailContextType,
  defaultInputState,
} from '../types';

const LogInWithEmailContext = createContext<LogInWithEmailContextType>({
  email: null,
  setEmail: () => {},
  screen: 'email',
  setScreen: () => {},
  valid: false,
  setValid: () => {},
  loading: false,
  setLoading: () => {},
});

interface Props {
  children: React.ReactNode;
}

function LogInWithEmailContextProvider({ children }: Props) {
  const [email, setEmail] = useState<LogInWithEmailContextType['email']>({
    ...defaultInputState<LogInWithEmailContextType['email']['value']>(''),
  });
  const [screen, setScreen] =
    useState<LogInWithEmailContextType['screen']>('email');
  const [valid, setValid] = useState<LogInWithEmailContextType['valid']>(false);
  const [loading, setLoading] =
    useState<LogInWithEmailContextType['loading']>(false);

  return (
    <LogInWithEmailContext.Provider
      value={{
        email,
        setEmail,
        screen,
        setScreen,
        valid,
        setValid,
        loading,
        setLoading,
      }}
    >
      {children}
    </LogInWithEmailContext.Provider>
  );
}

export { LogInWithEmailContext, LogInWithEmailContextProvider };
