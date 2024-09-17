import React from 'react';
import { GoogleOAuthProvider } from '@react-oauth/google';

interface Props {
  children: React.ReactNode;
}

function LogInWithGoogleProvider({ children }: Props) {
  return (
    <GoogleOAuthProvider clientId="CLIENT_ID">{children}</GoogleOAuthProvider>
  );
}

export { LogInWithGoogleProvider };
