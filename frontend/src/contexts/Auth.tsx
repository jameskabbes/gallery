import React, { useEffect, useState, createContext } from 'react';
import { AuthContext as AuthContextType } from '../types';
import { GoogleOAuthProvider } from '@react-oauth/google';

const AuthContext = createContext<AuthContextType>({
  token: null,
  user: null,
});

interface Props {
  children: React.ReactNode;
}

function AuthContextProvider({ children }: Props) {
  const [token, setToken] = useState<AuthContextType['token']>(null);
  const [user, setUser] = useState<AuthContextType['user']>(null);

  useEffect(() => {
    // Fetch the user's auth state
  }, []);

  return (
    <GoogleOAuthProvider clientId="1855778612-f8jc05eb675d4226q50kqea1vp354ra0.apps.googleusercontent.com">
      <AuthContext.Provider
        value={{
          token,
          user,
        }}
      >
        {children}
      </AuthContext.Provider>
    </GoogleOAuthProvider>
  );
}

export { AuthContext, AuthContextProvider };
