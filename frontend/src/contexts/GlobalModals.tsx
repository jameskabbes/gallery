import React, { useContext, useEffect } from 'react';
import {
  GlobalModalsContext as GlobalModalsContextType,
  GlobalModalsType,
} from '../types';
import { LogInContext, LogInContextProvider } from './LogIn';
import { SignUpContext, SignUpContextProvider } from './SignUp';
import {
  LogInWithEmailContext,
  LogInWithEmailContextProvider,
} from './LogInWithEmail';

const GlobalModalsContext = React.createContext<GlobalModalsContextType>({
  toggleModal: () => {},
});

interface Props {
  children: React.ReactNode;
}

function GlobalModalsContextProvider({ children }: Props) {
  const logInContext = useContext(LogInContext);
  const signUpContext = useContext(SignUpContext);
  const logInWithEmailContext = useContext(LogInWithEmailContext);

  const contextMap = new Map([
    ['logIn', logInContext],
    ['signUp', signUpContext],
    ['logInWithEmail', logInWithEmailContext],
  ]);

  function toggleModal(targetModal: GlobalModalsType) {
    for (const modal of contextMap.keys()) {
      if (modal !== targetModal) {
        contextMap.get(modal).dispatch({ type: 'SET_ACTIVE', payload: false });
      }
    }
    contextMap.get(targetModal).dispatch({ type: 'SET_ACTIVE', payload: true });
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
