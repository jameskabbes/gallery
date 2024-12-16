import React, { useContext, useEffect, useState } from 'react';
import { AuthModalsContextType, AuthModalsType } from '../types';

import { LogIn } from '../components/Auth/LogIn';
import { SignUp } from '../components/Auth/SignUp';
import { LogInWithEmail } from '../components/Auth/LogInWithEmail';
import { GlobalModalsContext } from './GlobalModals';

const AuthModalsContext = React.createContext<AuthModalsContextType>({
  activate: (authModalType) => {},
});

function AuthModalsContextProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const globalModalsContext = useContext(GlobalModalsContext);

  function activate(authModalType: AuthModalsType) {
    let _children: React.ReactNode = null;
    switch (authModalType) {
      case 'logIn':
        _children = <LogIn />;
        break;
      case 'signUp':
        _children = <SignUp />;
        break;
      case 'logInWithEmail':
        _children = <LogInWithEmail />;
        break;
    }

    globalModalsContext.setModal({
      children: _children,
      contentAdditionalClassName: 'max-w-[400px] w-full',
      modalKey: authModalType,
    });
  }

  return (
    <AuthModalsContext.Provider
      value={{
        activate,
      }}
    >
      {children}
    </AuthModalsContext.Provider>
  );
}

export { AuthModalsContext, AuthModalsContextProvider };
