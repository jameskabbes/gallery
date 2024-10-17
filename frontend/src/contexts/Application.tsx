import React from 'react';
import { DarkModeContextProvider } from './DarkMode';
import { GlobalModalsContextProvider } from './GlobalModals';
import { DeviceContextProvider } from './Device';
import { AuthContextProvider } from './Auth';
import { AuthModalsContextProvider } from './AuthModals';
import { SignUpContextProvider } from './SignUp';
import { LogInWithEmailContextProvider } from './LogInWithEmail';
import { EscapeKeyContextProvider } from './EscapeKey';
import { ToastContextProvider } from './Toast';
import { LogInWithGoogleProvider } from './LogInWithGoogle';
import { LogInContextProvider } from './LogIn';

const ApplicationContextProvider = ({ children }) => {
  return (
    <EscapeKeyContextProvider>
      <AuthContextProvider>
        <DeviceContextProvider>
          <GlobalModalsContextProvider>
            <DarkModeContextProvider>
              <LogInContextProvider>
                <LogInWithGoogleProvider>
                  <LogInWithEmailContextProvider>
                    <SignUpContextProvider>
                      <AuthModalsContextProvider>
                        <ToastContextProvider>{children}</ToastContextProvider>
                      </AuthModalsContextProvider>
                    </SignUpContextProvider>
                  </LogInWithEmailContextProvider>
                </LogInWithGoogleProvider>
              </LogInContextProvider>
            </DarkModeContextProvider>
          </GlobalModalsContextProvider>
        </DeviceContextProvider>
      </AuthContextProvider>
    </EscapeKeyContextProvider>
  );
};

export { ApplicationContextProvider };
