import React, { useEffect, useState, createContext } from 'react';
import { DarkModeContext as DarkModeContextType } from '../types';

const DarkModeContext = createContext<DarkModeContextType>({
  state: false,
  toggle: () => {},
});

interface Props {
  children: React.ReactNode;
}

function DarkModeContextProvider({ children }: Props) {
  const [state, setState] = useState(false);

  useEffect(() => {
    const stateMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    setState(stateMediaQuery.matches);

    const handlestatePreferenceChange = (e: MediaQueryListEvent) => {
      setState(e.matches);
    };

    stateMediaQuery.addEventListener('change', handlestatePreferenceChange);

    return () => {
      stateMediaQuery.removeEventListener(
        'change',
        handlestatePreferenceChange
      );
    };
  }, []);

  useEffect(() => {
    if (state) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [state]);

  const toggle = () => {
    setState(!state);
  };

  return (
    <DarkModeContext.Provider value={{ state, toggle }}>
      {children}
    </DarkModeContext.Provider>
  );
}

export { DarkModeContext, DarkModeContextProvider };
