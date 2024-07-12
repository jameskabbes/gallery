import React from 'react';
import { DarkModeToggle } from './DarkModeToggle';

function Header(): JSX.Element {
  return (
    <header>
      <div className="max-w-screen-2xl mx-auto flex flex-row justify-between items-center px-2 py-2">
        <p>Gallery</p>
        <div className="flex flex-row">
          <DarkModeToggle />
        </div>
      </div>
    </header>
  );
}

export { Header };
