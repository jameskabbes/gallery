import React from 'react';
import { DarkModeContextProvider } from './DarkMode';
import { DataContextProvider } from './Data';
import { ModalsContextProvider } from './Modals';
import { DeviceContextProvider } from './Device';
import { AuthContextProvider } from './Auth';
import { LoginContextProvider } from './Login';

const ApplicationContextProvider = ({ children }) => {
  return (
    <AuthContextProvider>
      <DeviceContextProvider>
        <DataContextProvider>
          <ModalsContextProvider>
            <DarkModeContextProvider>
              <LoginContextProvider>{children}</LoginContextProvider>
            </DarkModeContextProvider>
          </ModalsContextProvider>
        </DataContextProvider>
      </DeviceContextProvider>
    </AuthContextProvider>
  );
};

export { ApplicationContextProvider };
