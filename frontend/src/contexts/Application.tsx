import React from 'react';
import { DarkModeContextProvider } from './DarkMode';
import { DataContextProvider } from './Data';
import { ModalsContextProvider } from './Modals';
import { DeviceContextProvider } from './Device';
import { AuthContextProvider } from './Auth';

const ApplicationContextProvider = ({ children }) => {
  return (
    <AuthContextProvider>
      <DeviceContextProvider>
        <DataContextProvider>
          <ModalsContextProvider>
            <DarkModeContextProvider>{children}</DarkModeContextProvider>
          </ModalsContextProvider>
        </DataContextProvider>
      </DeviceContextProvider>
    </AuthContextProvider>
  );
};

export { ApplicationContextProvider };
