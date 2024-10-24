import React from 'react';
import { IoAperture } from 'react-icons/io5';
import { Menu } from './Menu';
import { Link } from 'react-router-dom';
import { DarkModeToggle } from './DarkModeToggle';
import { Surface } from './Utils/Surface';

function Header(): JSX.Element {
  return (
    <Surface>
      <header className="sticky top-0 surface bg-opacity-50 border-b-[1px]">
        <h6>
          <div className="max-w-screen-2xl mx-auto flex flex-row justify-between items-center px-2 py-2">
            <Link to="/">
              <span className="flex flex-row items-center space-x-1">
                <IoAperture />
                <span>Gallery</span>
              </span>
            </Link>
            <div className="flex flex-row items-center space-x-2">
              <DarkModeToggle />
              {/* <Menu /> */}
            </div>
          </div>
        </h6>
      </header>
    </Surface>
  );
}

export { Header };
