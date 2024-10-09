import React, { useContext, useEffect, useState } from 'react';
import {
  AuthModalsContext as AuthModalsContextType,
  AuthModalsType,
} from '../types';

const AuthModalsContext = React.createContext<AuthModalsContextType>({
  activeModalType: null,
  setActiveModalType: () => null,
});

interface Props {
  children: React.ReactNode;
}

function AuthModalsContextProvider({ children }: Props) {
  const [activeModalType, setActiveModalType] = useState<AuthModalsType | null>(
    null
  );

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
