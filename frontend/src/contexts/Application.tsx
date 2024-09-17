import React from 'react';
import { DarkModeContextProvider } from './DarkMode';
import { DataContextProvider } from './Data';
import { ModalsContextProvider } from './Modals';
import { DeviceContextProvider } from './Device';
import { AuthContextProvider } from './Auth';
import { GlobalModalsContextProvider } from './GlobalModals';
import { LogInContextProvider } from './LogIn';
import { SignUpContextProvider } from './SignUp';
import { LogInWithEmailContextProvider } from './LogInWithEmail';
import { EscapeKeyContextProvider } from './EscapeKey';
import { ToastContextProvider } from './Toast';

const ApplicationContextProvider = ({ children }) => {
  return (
    <EscapeKeyContextProvider>
      <AuthContextProvider>
        <DeviceContextProvider>
          <DataContextProvider>
            <ModalsContextProvider>
              <DarkModeContextProvider>
                <LogInContextProvider>
                  <LogInWithEmailContextProvider>
                    <SignUpContextProvider>
                      <GlobalModalsContextProvider>
                        <ToastContextProvider>{children}</ToastContextProvider>
                      </GlobalModalsContextProvider>
                    </SignUpContextProvider>
                  </LogInWithEmailContextProvider>
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
