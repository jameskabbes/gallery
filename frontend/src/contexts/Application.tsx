import React from 'react';
import { DarkModeContextProvider } from './DarkMode';
import { ModalsContextProvider } from './Modals';
import { DeviceContextProvider } from './Device';
import { AuthContextProvider } from './Auth';
import { AuthModalsContextProvider } from './AuthModals';
import { LogInContextProvider } from './LogIn';
import { SignUpContextProvider } from './SignUp';
import { LogInWithEmailContextProvider } from './LogInWithEmail';
import { EscapeKeyContextProvider } from './EscapeKey';
import { ToastContextProvider } from './Toast';
import { LogInWithGoogleProvider } from './LogInWithGoogle';

const ApplicationContextProvider = ({ children }) => {
  return (
    <EscapeKeyContextProvider>
      <AuthContextProvider>
        <DeviceContextProvider>
          <ModalsContextProvider>
            <DarkModeContextProvider>
              <LogInWithGoogleProvider>
                <LogInContextProvider>
                  <LogInWithEmailContextProvider>
                    <SignUpContextProvider>
                      <AuthModalsContextProvider>
                        <ToastContextProvider>{children}</ToastContextProvider>
                      </AuthModalsContextProvider>
                    </SignUpContextProvider>
                  </LogInWithEmailContextProvider>
                </LogInContextProvider>
              </LogInWithGoogleProvider>
            </DarkModeContextProvider>
          </ModalsContextProvider>
        </DeviceContextProvider>
      </AuthContextProvider>
    </EscapeKeyContextProvider>
  );
};

export { ApplicationContextProvider };
