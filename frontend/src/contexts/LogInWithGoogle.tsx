import React from 'react';
import { GoogleOAuthProvider } from '@react-oauth/google';

import google_client_secret from '../../../data/google_client_secret.json';

export function LogInWithGoogleProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <GoogleOAuthProvider clientId={google_client_secret['web']['client_id']}>
      {children}
    </GoogleOAuthProvider>
  );
}
