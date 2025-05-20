import React, { Component, useContext, useEffect, useState } from 'react';
import { AuthModalsContextType, AuthModalType, ModalType } from '../types';
import { ModalsContext } from './Modals';
import { LogIn } from '../components/Auth/LogIn';
import { RequestSignUp } from '../components/Auth/SignUp';
import { RequestMagicLink } from '../components/Auth/MagicLink';
import { RequestOTP, VerifyOTP } from '../components/Auth/OTP';

export const AuthModalsContext = React.createContext<AuthModalsContextType>({
  activate: () => {},
});

const authModalMapping: Record<AuthModalType, React.ComponentType> = {
  logIn: LogIn,
  requestSignUp: RequestSignUp,
  requestMagicLink: RequestMagicLink,
  requestOTP: RequestOTP,
  verifyOTP: VerifyOTP,
};

export function AuthModalsContextProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const modalsContext = useContext(ModalsContext);
  const [active, setActive] = useState<AuthModalType | null>(null);

  const activate: AuthModalsContextType['activate'] = (modalType) => {
    setActive((prev) => {
      if (modalType === null) {
        if (prev !== null) {
          modalsContext.deleteModals([prev]);
        }
      } else {
        const modal: ModalType = {
          key: modalType,
          contentAdditionalClassName: 'max-w-[400px] w-full',
          Component: authModalMapping[modalType],
          onExit: () => setActive(null),
        };

        if (prev) {
          modalsContext.swapActiveModal(modal);
        } else {
          modalsContext.pushModals([modal]);
        }
        return modalType;
      }
    });
  };

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
