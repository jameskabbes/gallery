import React, { useContext } from 'react';
import { DarkModeContext } from '../../contexts/DarkMode';

import { IoSunnyOutline } from 'react-icons/io5';
import { IoMoonOutline } from 'react-icons/io5';
import { IoSettingsOutline } from 'react-icons/io5';
import { DarkModeContext as DarkModeContextType } from '../../types';

interface ThemeOption {
  value: DarkModeContextType['preference'];
  icon: JSX.Element;
  label: string;
}

function DarkModeToggle() {
  // initialize dark mode with the client's system/app preferences

  const darkModeContext = useContext(DarkModeContext);
  const themeOptions: ThemeOption[] = [
    { value: 'light', icon: <IoSunnyOutline />, label: 'Light Mode' },
    { value: 'system', icon: <IoSettingsOutline />, label: 'System' },
    { value: 'dark', icon: <IoMoonOutline />, label: 'Dark Mode' },
  ];

  return (
    <>
      <h2>Theme</h2>
      {/* make a radio selector */}
      <form>
        {themeOptions.map((option) => (
          <label key={option.value}>
            <input
              type="radio"
              name="theme"
              value={option.value}
              checked={darkModeContext.preference === option.value}
              onChange={() => darkModeContext.setPreference(option.value)}
            />
            {option.label}
          </label>
        ))}
      </form>
    </>
  );
}

function Appearance() {
  const darkModeContext = useContext(DarkModeContext);

  return <DarkModeToggle />;
}

export { Appearance };
