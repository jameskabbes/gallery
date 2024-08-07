import React from 'react';
import { DarkModeContextProvider } from './DarkMode';
import { ConfirmationModalContextProvider } from './ConfirmationModal';
import { DataContextProvider } from './Data';
import { LoginContextProvider } from './Login';

const ApplicationContextProvider = ({ children }) => {
  return (
    <DataContextProvider>
      <LoginContextProvider>
        <ConfirmationModalContextProvider>
          <DarkModeContextProvider>{children}</DarkModeContextProvider>
        </ConfirmationModalContextProvider>
      </LoginContextProvider>
    </DataContextProvider>
  );
};

export { ApplicationContextProvider };
