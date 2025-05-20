import React from 'react';
import { DarkModeContextProvider } from './DarkMode';
import { ModalsContextProvider } from './Modals';
import { DeviceContextProvider } from './Device';
import { AuthContextProvider } from './Auth';
import { AuthModalsContextProvider } from './AuthModals';
import { RequestSignUpContextProvider } from './RequestSignUp';
import { RequestMagicLinkContextProvider } from './RequestMagicLink';
import { RequestOTPContextProvider } from './RequestOTP';
import { EscapeKeyContextProvider } from './EscapeKey';
import { ToastContextProvider } from './Toast';
import { LogInWithGoogleProvider } from './LogInWithGoogle';
import { LogInContextProvider } from './LogIn';

export const ApplicationContextProvider = ({ children }) => {
  return (
    <ToastContextProvider>
      <EscapeKeyContextProvider>
        <AuthContextProvider>
          <DeviceContextProvider>
            <ModalsContextProvider>
              <DarkModeContextProvider>
                <LogInContextProvider>
                  <LogInWithGoogleProvider>
                    <RequestMagicLinkContextProvider>
                      <RequestSignUpContextProvider>
                        <RequestOTPContextProvider>
                          <AuthModalsContextProvider>
                            {children}
                          </AuthModalsContextProvider>
                        </RequestOTPContextProvider>
                      </RequestSignUpContextProvider>
                    </RequestMagicLinkContextProvider>
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
