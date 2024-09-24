import React, { useContext } from 'react';
import { IoAperture } from 'react-icons/io5';
import { Menu } from './Menu';
import { Link } from 'react-router-dom';

function Header(): JSX.Element {
  return (
    <header className="sticky top-0 bg-light dark:bg-dark bg-opacity-50">
      <div className="max-w-screen-2xl mx-auto flex flex-row justify-between items-center px-2 py-2">
        <Link to="/">
          <h5 className="mb-0">
            <span className="flex flex-row items-center space-x-1">
              <IoAperture />
              <span>Gallery</span>
            </span>
          </h5>
        </Link>
        <div className="flex flex-row items-center space-x-2">
          <Menu />
        </div>
      </div>
      <hr />
    </header>
  );
}

export { Header };
