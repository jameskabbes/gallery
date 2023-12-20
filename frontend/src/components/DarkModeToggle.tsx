import React, { useEffect, useState } from 'react';
import { useDarkMode } from '../utils/useDarkMode';

import { MdOutlineDarkMode } from 'react-icons/md';
import { HiOutlineSun } from 'react-icons/hi';
import { BsToggleOn, BsToggleOff } from 'react-icons/bs';

const DarkModeToggle = () => {
  // initialize dark mode with the client's system/app preferences
  const [darkMode, setDarkMode] = useState(useDarkMode());

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  return (
    <div
      onClick={toggleDarkMode}
      className="flex flex-row space-x-1 cursor-pointer"
    >
      {darkMode ? (
        <>
          <MdOutlineDarkMode size={20} />
          <BsToggleOn size={20} />
        </>
      ) : (
        <>
          <HiOutlineSun size={20} />
          <BsToggleOff size={20} />
        </>
      )}
    </div>
  );
};

export { DarkModeToggle };
