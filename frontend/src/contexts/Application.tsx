import React from 'react';
import { DarkModeContextProvider } from './DarkMode';
import { DataContextProvider } from './Data';
import { ModalsContextProvider } from './Modals';

const ApplicationContextProvider = ({ children }) => {
  return (
    <DataContextProvider>
      <ModalsContextProvider>
        <DarkModeContextProvider>{children}</DarkModeContextProvider>
      </ModalsContextProvider>
    </DataContextProvider>
  );
};

export { ApplicationContextProvider };
