import React, { useEffect, useState, createContext } from 'react';
import { AuthContext as AuthContextType } from '../types';

const AuthContext = createContext<AuthContextType>({
  user: null,
});

interface Props {
  children: React.ReactNode;
}

function AuthContextProvider({ children }: Props) {
  const [user, setUser] = useState<AuthContextType['user']>(null);

  useEffect(() => {
    // Fetch the user's auth state
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export { AuthContext, AuthContextProvider };
