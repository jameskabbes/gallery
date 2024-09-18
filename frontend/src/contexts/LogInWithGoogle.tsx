import React from 'react';
import { GoogleOAuthProvider } from '@react-oauth/google';

import google_client_secret from '../../../data/google_client_secret.json';

interface Props {
  children: React.ReactNode;
}

function LogInWithGoogleProvider({ children }: Props) {
  return (
    <GoogleOAuthProvider clientId={google_client_secret['web']['client_id']}>
      {children}
    </GoogleOAuthProvider>
  );
}

export { LogInWithGoogleProvider };
