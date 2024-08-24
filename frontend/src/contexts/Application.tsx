import React from 'react';
import { DarkModeContextProvider } from './DarkMode';
import { DataContextProvider } from './Data';
import { ModalsContextProvider } from './Modals';
import { DeviceContextProvider } from './Device';
import { AuthContextProvider } from './Auth';
import { LogInContextProvider } from './LogIn';
import { SignUpContextProvider } from './SignUp';

const ApplicationContextProvider = ({ children }) => {
  return (
    <AuthContextProvider>
      <DeviceContextProvider>
        <DataContextProvider>
          <ModalsContextProvider>
            <DarkModeContextProvider>
              <SignUpContextProvider>
                <LogInContextProvider>{children}</LogInContextProvider>
              </SignUpContextProvider>
            </DarkModeContextProvider>
          </ModalsContextProvider>
        </DataContextProvider>
      </DeviceContextProvider>
    </AuthContextProvider>
  );
};

export { ApplicationContextProvider };
