import React from 'react';
import { DarkModeContextProvider } from './DarkMode';
import { DataContextProvider } from './Data';
import { ModalsContextProvider } from './Modals';
import { DeviceContextProvider } from './Device';

const ApplicationContextProvider = ({ children }) => {
  return (
    <DeviceContextProvider>
      <DataContextProvider>
        <ModalsContextProvider>
          <DarkModeContextProvider>{children}</DarkModeContextProvider>
        </ModalsContextProvider>
      </DataContextProvider>
    </DeviceContextProvider>
  );
};

export { ApplicationContextProvider };
