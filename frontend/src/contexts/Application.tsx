import React from 'react';
import { DarkModeContextProvider } from './DarkMode';
import { ModalsContextProvider } from './Modals';
import { DeviceContextProvider } from './Device';
import { AuthContextProvider } from './Auth';
import { AuthModalsContextProvider } from './AuthModals';
import { RequestSignUpContextProvider } from './RequestSignUp';
import { SendMagicLinkContextProvider } from './SendMagicLink';
import { EscapeKeyContextProvider } from './EscapeKey';
import { ToastContextProvider } from './Toast';
import { LogInWithGoogleProvider } from './LogInWithGoogle';
import { LogInContextProvider } from './LogIn';

const ApplicationContextProvider = ({ children }) => {
  return (
    <ToastContextProvider>
      <EscapeKeyContextProvider>
        <AuthContextProvider>
          <DeviceContextProvider>
            <ModalsContextProvider>
              <DarkModeContextProvider>
                <LogInContextProvider>
                  <LogInWithGoogleProvider>
                    <SendMagicLinkContextProvider>
                      <RequestSignUpContextProvider>
                        <AuthModalsContextProvider>
                          {children}
                        </AuthModalsContextProvider>
                      </RequestSignUpContextProvider>
                    </SendMagicLinkContextProvider>
                  </LogInWithGoogleProvider>
                </LogInContextProvider>
              </DarkModeContextProvider>
            </ModalsContextProvider>
          </DeviceContextProvider>
        </AuthContextProvider>
      </EscapeKeyContextProvider>
    </ToastContextProvider>
  );
};

export { ApplicationContextProvider };
