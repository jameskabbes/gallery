import React from 'react';
import { DarkModeContextProvider } from './DarkMode';
import { ConfirmationModalContextProvider } from './ConfirmationModal';
import { DataContextProvider } from './Data';
import { ToastContextProvider } from './Toast';

const ApplicationContextProvider = ({ children }) => {
  return (
    <DataContextProvider>
      <ToastContextProvider>
        <ConfirmationModalContextProvider>
          <DarkModeContextProvider>{children}</DarkModeContextProvider>
        </ConfirmationModalContextProvider>
      </ToastContextProvider>
    </DataContextProvider>
  );
};

export { ApplicationContextProvider };
