import React, { useEffect } from 'react';
import {
  GlobalModalsContext as GlobalModalsContextType,
  GlobalModalsType,
} from '../types';
import { LogInContext, LogInContextProvider } from './LogIn_';
import { SignUpContext, SignUpContextProvider } from './SignUp';

const GlobalModalsContext = React.createContext<GlobalModalsContextType>({
  toggleModal: () => {},
});

interface Props {
  children: React.ReactNode;
}

function GlobalModalsContextProvider({ children }: Props) {
  const logInContext = React.useContext(LogInContext);
  const signUpContext = React.useContext(SignUpContext);

  function toggleModal(modal: GlobalModalsType) {
    if (modal === 'logIn') {
      signUpContext.dispatch({ type: 'SET_ACTIVE', payload: false });
      logInContext.dispatch({ type: 'SET_ACTIVE', payload: true });
    } else if (modal === 'signUp') {
      logInContext.dispatch({ type: 'SET_ACTIVE', payload: false });
      signUpContext.dispatch({ type: 'SET_ACTIVE', payload: true });
    }
  }

  return (
    <GlobalModalsContext.Provider
      value={{
        toggleModal,
      }}
    >
      {children}
    </GlobalModalsContext.Provider>
  );
}

export { GlobalModalsContext, GlobalModalsContextProvider };
