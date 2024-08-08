import React from 'react';
import { DarkModeContextProvider } from './DarkMode';
import { DataContextProvider } from './Data';
import { ModalContextProvider } from './Modal';

const ApplicationContextProvider = ({ children }) => {
  return (
    <DataContextProvider>
      <ModalContextProvider>
        <DarkModeContextProvider>{children}</DarkModeContextProvider>
      </ModalContextProvider>
    </DataContextProvider>
  );
};

export { ApplicationContextProvider };
