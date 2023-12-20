import React from 'react';
import { NavBar } from './NavBar';
import { DarkModeToggle } from './DarkModeToggle';

function Header() {
  return (
    <header>
      <div className="flex flex-row justify-between items-center px-2 py-2">
        <div className="flex flex-row">
          <NavBar />
        </div>
        <div className="flex flex-row">
          <DarkModeToggle />
        </div>
      </div>
    </header>
  );
}

export { Header };
