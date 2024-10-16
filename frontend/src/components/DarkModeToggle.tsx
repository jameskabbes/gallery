import React, { useContext } from 'react';
import { IoMoon } from 'react-icons/io5';
import { IoMoonOutline } from 'react-icons/io5';
import { DarkModeContext } from '../contexts/DarkMode';

function DarkModeToggle() {
  const darkModeContext = useContext(DarkModeContext);

  return (
    <button
      className="button-icon"
      onClick={() => {
        // current state is dark mode
        if (darkModeContext.state) {
          darkModeContext.setPreference('light');
        } else {
          darkModeContext.setPreference('dark');
        }
      }}
    >
      {darkModeContext.state ? <IoMoon /> : <IoMoonOutline />}
    </button>
  );
}

export { DarkModeToggle };
