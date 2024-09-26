import React, { useContext, useEffect } from 'react';
import {
  AuthModalsContext as AuthModalsContextType,
  AuthModalsType,
  LogInContext as LogInContextType,
  SignUpContext as SignUpContextType,
  LogInWithEmailContext as LogInWithEmailContextType,
} from '../types';
import { LogInContext, LogInContextProvider } from './LogIn';
import { SignUpContext, SignUpContextProvider } from './SignUp';
import {
  LogInWithEmailContext,
  LogInWithEmailContextProvider,
} from './LogInWithEmail';

const AuthModalsContext = React.createContext<AuthModalsContextType>({
  toggleModal: () => {},
});

interface Props {
  children: React.ReactNode;
}

function AuthModalsContextProvider({ children }: Props) {
  const logInContext = useContext(LogInContext);
  const signUpContext = useContext(SignUpContext);
  const logInWithEmailContext = useContext(LogInWithEmailContext);

  // Example usage
  const contextMap = new Map<
    AuthModalsType,
    LogInContextType | SignUpContextType | LogInWithEmailContextType
  >([
    ['logIn', logInContext],
    ['signUp', signUpContext],
    ['logInWithEmail', logInWithEmailContext],
  ]);

  function toggleModal(targetModal: AuthModalsType) {
    console.log('toggleModal', targetModal);
    for (const modal of contextMap.keys()) {
      if (modal !== targetModal) {
        contextMap.get(modal).dispatch({ type: 'SET_ACTIVE', payload: false });
      }
    }
    contextMap.get(targetModal).dispatch({ type: 'SET_ACTIVE', payload: true });
  }

  return (
    <AuthModalsContext.Provider
      value={{
        toggleModal,
      }}
    >
      {children}
    </AuthModalsContext.Provider>
  );
}

export { AuthModalsContext, AuthModalsContextProvider };
