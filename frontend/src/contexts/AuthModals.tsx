import React, { useContext, useEffect } from 'react';
import {
  AuthModalsContext as AuthModalsContextType,
  AuthModalsType,
  LogInContext as LogInContextType,
  SignUpContext as SignUpContextType,
  LogInWithEmailContext as LogInWithEmailContextType,
} from '../types';

const AuthModalsContext = React.createContext<AuthModalsContextType>({
  activeModalType: null,
  setActiveModalType: () => null,
});

interface Props {
  children: React.ReactNode;
}

function AuthModalsContextProvider({ children }: Props) {
  const [activeModalType, setActiveModalType] =
    React.useState<AuthModalsType | null>(null);

  return (
    <AuthModalsContext.Provider
      value={{
        activeModalType,
        setActiveModalType,
      }}
    >
      {children}
    </AuthModalsContext.Provider>
  );
}

export { AuthModalsContext, AuthModalsContextProvider };
