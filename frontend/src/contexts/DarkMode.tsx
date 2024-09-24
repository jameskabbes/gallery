import React, { useEffect, useState, createContext } from 'react';
import { DarkModeContext as DarkModeContextType } from '../types';

const localStorageKey = 'theme';

const localStoragePreference: DarkModeContextType['preference'] =
  (localStorage.getItem(
    localStorageKey
  ) as DarkModeContextType['preference']) || 'system';

const DarkModeContext = createContext<DarkModeContextType>({
  state: false,
  preference: localStoragePreference,
  setPreference: (preference: DarkModeContextType['preference']) => {},
});

interface Props {
  children: React.ReactNode;
}

function DarkModeContextProvider({ children }: Props) {
  const [state, setState] = useState(false);
  const [systemState, setSystemState] = useState(false);
  const [preference, setPreference] = useState<
    DarkModeContextType['preference']
  >(localStoragePreference);

  // update the system state
  useEffect(() => {
    const stateMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    setSystemState(stateMediaQuery.matches);

    const handlestatePreferenceChange = (e: MediaQueryListEvent) => {
      setSystemState(e.matches);
    };

    stateMediaQuery.addEventListener('change', handlestatePreferenceChange);

    return () => {
      stateMediaQuery.removeEventListener(
        'change',
        handlestatePreferenceChange
      );
    };
  }, []);

  // as the state changes, store the preference in localStorage
  useEffect(() => {
    localStorage.setItem(localStorageKey, preference);
  }, [preference]);

  // as the state changes, update the classlist
  useEffect(() => {
    if (state) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [state]);

  // update the state based on the preference
  useEffect(() => {
    if (preference === 'light') {
      setState(false);
    } else if (preference === 'dark') {
      setState(true);
    } else {
      setState(systemState);
    }
  }, [preference, systemState]);

  return (
    <DarkModeContext.Provider value={{ state, preference, setPreference }}>
      {children}
    </DarkModeContext.Provider>
  );
}

export { DarkModeContext, DarkModeContextProvider };
