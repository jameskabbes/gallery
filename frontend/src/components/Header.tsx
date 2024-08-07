import React, { useContext } from 'react';
import { DarkModeToggle } from './DarkModeToggle';
import { LoginContext } from '../contexts/Login';

function Header(): JSX.Element {
  let loginContext = useContext(LoginContext);

  return (
    <header>
      <div className="max-w-screen-2xl mx-auto flex flex-row justify-between items-center px-2 py-2">
        <p>Gallery</p>
        <div className="flex flex-row items-center space-x-2">
          <DarkModeToggle />
          <button onClick={loginContext.toggle}>Login</button>
        </div>
      </div>
    </header>
  );
}

export { Header };
