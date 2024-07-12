import React from 'react';
import { DarkModeContextProvider } from './DarkMode';
import { ConfirmationModalContextProvider } from './ConfirmationModal';

const ApplicationContextProvider = ({ children }) => {
  return (
    <ConfirmationModalContextProvider>
      <DarkModeContextProvider>{children}</DarkModeContextProvider>
    </ConfirmationModalContextProvider>
  );
};

export { ApplicationContextProvider };
