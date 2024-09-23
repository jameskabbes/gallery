import React, { useState, useEffect, useRef, useContext } from 'react';
import { IoPersonCircleOutline } from 'react-icons/io5';
import { IoMenuSharp } from 'react-icons/io5';
import { Link } from 'react-router-dom';

import { useClickOutside } from '../utils/useClickOutside';
import { GlobalModalsContext } from '../contexts/AuthModals';
import { ToastContext } from '../contexts/Toast';
import { AuthContext } from '../contexts/Auth';
import { logOut } from './Auth/logout';

function AccountIcon() {
  const [isMenuVisible, setIsMenuVisible] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const authContext = useContext(AuthContext);
  const globalModalsContext = useContext(GlobalModalsContext);
  const toastContext = useContext(ToastContext);
  useClickOutside(menuRef, () => setIsMenuVisible(false));

  const toggleMenu = () => {
    setIsMenuVisible(!isMenuVisible);
  };

  const menuItems = authContext.state.user
    ? [
        {
          element: <Link to="/profile">Profile</Link>,
          onClick: () => {},
        },
        {
          element: <span>Log Out</span>,
          onClick: () => {
            setIsMenuVisible(false);
            logOut(authContext, toastContext);
          },
        },
      ]
    : [
        {
          element: <span>Log In</span>,
          onClick: () => {
            setIsMenuVisible(false);
            globalModalsContext.toggleModal('logIn');
          },
        },
        {
          element: <span>Sign Up</span>,
          onClick: () => {
            setIsMenuVisible(false);
            globalModalsContext.toggleModal('signUp');
          },
        },
      ];

  return (
    <div className="relative" ref={menuRef}>
      <button
        className="flex flex-row rounded-full border-2 p-2 items-center space-x-1"
        onClick={toggleMenu}
      >
        <IoMenuSharp />
        <IoPersonCircleOutline />
      </button>
      {isMenuVisible && (
        <div
          className="absolute right-0 mt-2 w-48 bg-inherit border-2 rounded-xl shadow-2xl"
          ref={menuRef}
        >
          <ul className="flex flex-col">
            <ul className="flex flex-col">
              {menuItems.map((item, index) => (
                <li
                  key={index}
                  className="px-4 py-2 hover:bg-gray-100 cursor-pointer"
                  onClick={item.onClick}
                >
                  {item.element}
                </li>
              ))}
            </ul>
          </ul>
        </div>
      )}
    </div>
  );
}

export { AccountIcon };
