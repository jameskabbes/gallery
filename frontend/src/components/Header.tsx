import React, { useContext } from 'react';
import { DarkModeToggle } from './DarkModeToggle';
import { ModalContext } from '../contexts/Modal';
import { Login } from './Login';

function Header(): JSX.Element {
  let modalContext = useContext(ModalContext);

  return (
    <header>
      <div className="max-w-screen-2xl mx-auto flex flex-row justify-between items-center px-2 py-2">
        <p>Gallery</p>
        <div className="flex flex-row items-center space-x-2">
          <DarkModeToggle />
          <button
            onClick={() =>
              modalContext.dispatch({ type: 'PUSH', payload: <Login /> })
            }
          >
            Sign In
          </button>
        </div>
      </div>
    </header>
  );
}

export { Header };
