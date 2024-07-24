import React from 'react';
import { DarkModeContextProvider } from './DarkMode';
import { ConfirmationModalContextProvider } from './ConfirmationModal';
import { DataContextProvider } from './Data';

const ApplicationContextProvider = ({ children }) => {
  return (
    <DataContextProvider>
      <ConfirmationModalContextProvider>
        <DarkModeContextProvider>{children}</DarkModeContextProvider>
      </ConfirmationModalContextProvider>
    </DataContextProvider>
  );
};

export { ApplicationContextProvider };
