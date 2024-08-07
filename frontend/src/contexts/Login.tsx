import React, { useEffect, useState, createContext } from 'react';
import { LoginContext as LoginContextType } from '../types';

const LoginContext = createContext<LoginContextType>({
  state: false,
  toggle: () => {},
});

interface Props {
  children: React.ReactNode;
}

function LoginContextProvider({ children }: Props) {
  const [state, setState] = useState(false);
  const toggle = () => {
    setState(!state);
  };

  return (
    <LoginContext.Provider value={{ state, toggle }}>
      {children}
    </LoginContext.Provider>
  );
}

export { LoginContext, LoginContextProvider };
