import React, { useContext } from 'react';
import { DarkModeToggle } from './DarkModeToggle';
import { ModalsContext } from '../contexts/Modals';
import { Login } from './Login';
import { IoAperture } from 'react-icons/io5';

import { AccountIcon } from './AccountIcon';

function Header(): JSX.Element {
  let modalsContext = useContext(ModalsContext);

  return (
    <header className="sticky top-0 bg-light dark:bg-dark bg-opacity-50">
      <div className="max-w-screen-2xl mx-auto flex flex-row justify-between items-center px-2 py-2">
        <h5 className="mb-0">
          <span className="flex flex-row items-center space-x-2">
            <IoAperture />
            <span>Gallery</span>
          </span>
        </h5>
        <div className="flex flex-row items-center space-x-2">
          <h6 className="mb-0">
            <DarkModeToggle />
          </h6>

          <button
            className="button-primary"
            onClick={() =>
              modalsContext.dispatch({ type: 'PUSH', payload: <Login /> })
            }
          >
            <p>Sign In</p>
          </button>
          <button>
            <AccountIcon />
          </button>
        </div>
      </div>
      <hr />
    </header>
  );
}

export { Header };
