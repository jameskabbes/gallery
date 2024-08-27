import React from 'react';
import { DarkModeContextProvider } from './DarkMode';
import { DataContextProvider } from './Data';
import { ModalsContextProvider } from './Modals';
import { DeviceContextProvider } from './Device';
import { AuthContextProvider } from './Auth';
import { GlobalModalsContextProvider } from './GlobalModals';
import { LogInContextProvider } from './LogIn';
import { SignUpContextProvider } from './SignUp';
import { EscapeKeyContextProvider } from './EscapeKey';

const ApplicationContextProvider = ({ children }) => {
  return (
    <EscapeKeyContextProvider>
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
    </EscapeKeyContextProvider>
  );
};

export { ApplicationContextProvider };
