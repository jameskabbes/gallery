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

// import React, { useEffect, useState, createContext } from 'react';
// import { DarkModeContext as DarkModeContextType } from '../types';

// const DarkModeContext = createContext<DarkModeContextType>({
//   mode: 'system', // default to system
//   toggle: () => {},
//   setMode: (mode: 'light' | 'dark' | 'system') => {},
// });

// interface Props {
//   children: React.ReactNode;
// }

// function DarkModeContextProvider({ children }: Props) {
//   const [mode, setMode] = useState<'light' | 'dark' | 'system'>('system');

//   useEffect(() => {
//     // Check localStorage for saved user preference
//     const savedMode = localStorage.getItem('themeMode') as 'light' | 'dark' | 'system';
//     if (savedMode) {
//       setMode(savedMode);
//     }
//   }, []);

//   useEffect(() => {
//     const stateMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

//     const applyTheme = (theme: 'light' | 'dark' | 'system') => {
//       if (theme === 'dark' || (theme === 'system' && stateMediaQuery.matches)) {
//         document.documentElement.classList.add('dark');
//       } else {
//         document.documentElement.classList.remove('dark');
//       }
//     };

//     // Apply the theme based on the mode
//     applyTheme(mode);

//     const handleSystemPreferenceChange = (e: MediaQueryListEvent) => {
//       if (mode === 'system') {
//         applyTheme('system');
//       }
//     };

//     // Listen for changes in system preference if the mode is 'system'
//     stateMediaQuery.addEventListener('change', handleSystemPreferenceChange);

//     return () => {
//       stateMediaQuery.removeEventListener('change', handleSystemPreferenceChange);
//     };
//   }, [mode]);

//   // Toggle function (can be adjusted as needed)
//   const toggle = () => {
//     if (mode === 'light') setMode('dark');
//     else if (mode === 'dark') setMode('system');
//     else setMode('light');
//   };

//   // Directly set the mode and save to localStorage
//   const updateMode = (newMode: 'light' | 'dark' | 'system') => {
//     setMode(newMode);
//     localStorage.setItem('themeMode', newMode); // Persist the choice
//   };

//   return (
//     <DarkModeContext.Provider value={{ mode, toggle, setMode: updateMode }}>
//       {children}
//     </DarkModeContext.Provider>
//   );
// }

// export { DarkModeContext, DarkModeContextProvider };
