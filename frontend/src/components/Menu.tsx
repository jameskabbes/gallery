import React, { useState, useEffect, useRef, useContext } from 'react';
import { IoPersonCircleOutline } from 'react-icons/io5';
import { IoMenuSharp } from 'react-icons/io5';
import { Link } from 'react-router-dom';

import { useClickOutside } from '../utils/useClickOutside';
import { AuthModalsContext } from '../contexts/AuthModals';
import { ToastContext } from '../contexts/Toast';
import { AuthContext } from '../contexts/Auth';
import { logOut } from './Auth/logOut';

function Menu() {
  const [isMenuVisible, setIsMenuVisible] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const authContext = useContext(AuthContext);
  const authModalsContext = useContext(AuthModalsContext);
  const toastContext = useContext(ToastContext);
  useClickOutside(menuRef, () => setIsMenuVisible(false));

  const toggleMenu = () => {
    setIsMenuVisible(!isMenuVisible);
  };

  const menuItems = authContext.state.user
    ? [
        {
          element: <Link to="/settings">Settings</Link>,
          onClick: () => {},
        },
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
          element: <Link to="/settings">Settings</Link>,
          onClick: () => {},
        },
        {
          element: <span>Log In</span>,
          onClick: () => {
            setIsMenuVisible(false);
            authModalsContext.setActiveModalType('logIn');
          },
        },
        {
          element: <span>Sign Up</span>,
          onClick: () => {
            setIsMenuVisible(false);
            authModalsContext.setActiveModalType('signUp');
          },
        },
      ];

  return (
    <div className="relative" ref={menuRef}>
      <h6 className="mb-0" onClick={toggleMenu}>
        <IoMenuSharp />
      </h6>
      {isMenuVisible && (
        <div
          className="surface absolute right-0 mt-2 w-48 border-2 rounded-xl shadow-2xl"
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

export { Menu };
