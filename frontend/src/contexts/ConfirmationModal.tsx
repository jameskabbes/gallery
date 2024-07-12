import React, { useEffect, useState, createContext } from 'react';
import { ConfirmationModalContext as ConfirmationModalContextType } from '../types';

const defaultContextValue: ConfirmationModalContextType = {
  isActive: false,
  isConfirmed: null,
  title: null,
  message: null,
  setIsActive: () => {},
  confirm: () => {},
  cancel: () => {},
  reset: () => {},
  setTitle: () => {},
  setMessage: () => {},
};

const ConfirmationModalContext = createContext<ConfirmationModalContextType>({
  ...defaultContextValue,
});

interface Props {
  children: React.ReactNode;
}

function ConfirmationModalContextProvider({ children }: Props) {
  const [isActive, setIsActive] = useState<
    ConfirmationModalContextType['isActive']
  >(defaultContextValue.isActive);
  const [isConfirmed, setIsConfirmed] = useState<
    ConfirmationModalContextType['isConfirmed']
  >(defaultContextValue.isConfirmed);
  const [title, setTitle] = useState<ConfirmationModalContextType['title']>(
    defaultContextValue.title
  );
  const [message, setMessage] = useState<
    ConfirmationModalContextType['message']
  >(defaultContextValue.message);

  function confirm() {
    setIsActive(false);
    setIsConfirmed(true);
  }

  function cancel() {
    setIsActive(false);
    setIsConfirmed(false);
  }

  function reset() {
    setIsConfirmed(null);
  }

  return (
    <ConfirmationModalContext.Provider
      value={{
        isActive,
        isConfirmed,
        title,
        message,
        setIsActive,
        confirm,
        cancel,
        reset,
        setTitle,
        setMessage,
      }}
    >
      {children}
    </ConfirmationModalContext.Provider>
  );
}

export { ConfirmationModalContext, ConfirmationModalContextProvider };
