import React, {
  createContext,
  useContext,
  useEffect,
  useCallback,
  useRef,
} from 'react';

import { EscapeKeyContextType } from '../types';

export const EscapeKeyContext = createContext<EscapeKeyContextType>({
  addCallback: () => {},
  removeCallback: () => {},
});

export function EscapeKeyContextProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const callbacks = useRef<Set<() => void>>(new Set());

  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (event.key === 'Escape') {
      callbacks.current.forEach((callback) => callback());
    }
  }, []);

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleKeyDown]);

  const addCallback = useCallback((callback: () => void) => {
    callbacks.current.add(callback);
  }, []);

  const removeCallback = useCallback((callback: () => void) => {
    callbacks.current.delete(callback);
  }, []);

  return (
    <EscapeKeyContext.Provider value={{ addCallback, removeCallback }}>
      {children}
    </EscapeKeyContext.Provider>
  );
}

export function useEscapeKey(callback: () => void) {
  const context = useContext(EscapeKeyContext);
  useEffect(() => {
    context.addCallback(callback);
    return () => {
      context.removeCallback(callback);
    };
  }, [callback, context]);
}
