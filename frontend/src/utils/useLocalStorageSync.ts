import { useEffect, useContext } from 'react';
import { AuthContext } from '../contexts/Auth';
import { AuthContext as AuthContextType } from '../types';

interface LocalStorageContexts {
  auth: AuthContextType;
}

function useLocalStorageSync() {
  const localStorageKeyContextMapping: LocalStorageContexts = {
    auth: useContext(AuthContext),
  };

  function handleStorageEvent(event: StorageEvent) {
    if (event.key && event.key in localStorageKeyContextMapping) {
      const newValue = event.newValue ? JSON.parse(event.newValue) : null;
      localStorageKeyContextMapping[event.key].setState(newValue);
    }
  }

  useEffect(() => {
    window.addEventListener('storage', handleStorageEvent);
    return () => {
      window.removeEventListener('storage', handleStorageEvent);
    };
  }, []);
}

export { useLocalStorageSync };
