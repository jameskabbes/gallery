import React, { useContext } from 'react';
import { IoAperture } from 'react-icons/io5';
import { Menu } from './Menu';
import { Link } from 'react-router-dom';
import { DarkModeToggle } from './DarkModeToggle';
import { Surface } from './Utils/Surface';
import { DeviceContext } from '../contexts/Device';
import { zIndex } from '../config/constants';

export function Header(): JSX.Element {
  const deviceContext = useContext(DeviceContext);

  return (
    <Surface>
      <header
        id="header"
        className="top-0 bg-opacity-50 border-b-[1px] sticky"
        style={{
          zIndex: zIndex.header,
        }}
      >
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
              <Menu />
            </div>
          </div>
        </h6>
      </header>
    </Surface>
  );
}
