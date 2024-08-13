import React, { useContext } from 'react';
import { DarkModeContext } from '../contexts/DarkMode';

import { MdOutlineDarkMode } from 'react-icons/md';
import { HiOutlineSun } from 'react-icons/hi';
import { BsToggleOn, BsToggleOff } from 'react-icons/bs';

function DarkModeToggle() {
  // initialize dark mode with the client's system/app preferences
  const { state, toggle } = useContext(DarkModeContext);

  return (
    <button className="flex flex-row space-x-1" onClick={toggle}>
      {state ? (
        <>
          <MdOutlineDarkMode />
          <BsToggleOn />
        </>
      ) : (
        <>
          <HiOutlineSun />
          <BsToggleOff />
        </>
      )}
    </button>
  );
}

export { DarkModeToggle };
