import React from 'react';
import { DarkModeContextProvider } from './DarkMode';
import { DataContextProvider } from './Data';
import { ModalsContextProvider } from './Modals';
import { DeviceContextProvider } from './Device';
import { AuthContextProvider } from './Auth';
import { GlobalModalsContextProvider } from './GlobalModals';
import { LogInContextProvider } from './LogIn_';
import { SignUpContextProvider } from './SignUp';

const ApplicationContextProvider = ({ children }) => {
  return (
    <AuthContextProvider>
      <DeviceContextProvider>
        <DataContextProvider>
          <ModalsContextProvider>
            <DarkModeContextProvider>
              <LogInContextProvider>
                <SignUpContextProvider>
                  <GlobalModalsContextProvider>
                    {children}
                  </GlobalModalsContextProvider>
                </SignUpContextProvider>
              </LogInContextProvider>
            </DarkModeContextProvider>
          </ModalsContextProvider>
        </DataContextProvider>
      </DeviceContextProvider>
    </AuthContextProvider>
  );
};

export { ApplicationContextProvider };
