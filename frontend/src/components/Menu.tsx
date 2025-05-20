import React, { useState, useEffect, useRef, useContext } from 'react';
import { IoPersonCircleOutline } from 'react-icons/io5';
import { IoMenuSharp } from 'react-icons/io5';
import { Link } from 'react-router-dom';

import { useClickOutside } from '../utils/useClickOutside';
import { AuthModalsContext } from '../contexts/AuthModals';
import { ToastContext } from '../contexts/Toast';
import { AuthContext } from '../contexts/Auth';
import { logOut } from './Auth/logOut';
import { Surface } from './Utils/Surface';
import { useConfirmationModal } from '../utils/useConfirmationModal';
import { config } from '../config/config';

export function Menu() {
  const [isMenuVisible, setIsMenuVisible] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const authContext = useContext(AuthContext);
  const authModalsContext = useContext(AuthModalsContext);
  const toastContext = useContext(ToastContext);
  useClickOutside(menuRef, () => setIsMenuVisible(false));
  const { activateButtonConfirmation } = useConfirmationModal();

  const toggleMenu = () => {
    setIsMenuVisible((prev) => !prev);
  };

  interface MenuItem {
    key: string;
    element: JSX.Element;
    onClick: () => void;
    viewMode?: 'logged-out' | 'logged-in' | 'both';
  }

  const menuItems: MenuItem[] = [
    {
      key: 'galleries',
      element: <Link to={config.frontendRoutes.galleries}>Galleries</Link>,
      onClick: () => {},
      viewMode: 'logged-in',
    },
    {
      key: 'settings',
      element: <Link to="/settings">Settings</Link>,
      onClick: () => {},
      viewMode: 'both',
    },
    {
      key: 'log-in',
      element: <span>Log In</span>,
      onClick: () => {
        setIsMenuVisible(false);
        authModalsContext.activate('logIn');
      },
      viewMode: 'logged-out',
    },
    {
      key: 'sign-up',
      element: <span>Sign Up</span>,
      onClick: () => {
        setIsMenuVisible(false);
        authModalsContext.activate('requestSignUp');
      },
      viewMode: 'logged-out',
    },
    {
      key: 'log-out',
      element: <span>Log Out</span>,
      onClick: () => {
        activateButtonConfirmation({
          componentProps: {
            title: 'Log Out?',
            confirmText: 'Log Out',
            message: 'Are you sure you want to log out?',
            onConfirm: () => {
              setIsMenuVisible(false);
              logOut(authContext, toastContext);
            },
          },
        });
      },
      viewMode: 'logged-in',
    },
  ];

  return (
    <div className="relative" ref={menuRef}>
      <button onClick={toggleMenu} className="flex flex-row items-center">
        <IoMenuSharp />
      </button>
      {isMenuVisible && (
        <Surface>
          <div
            className="absolute right-0 mt-2 border-[1px] rounded-xl shadow-2xl"
            ref={menuRef}
          >
            <ul className="flex flex-col space-y-1 m-2">
              {menuItems.map((item, index) => {
                if (
                  item.viewMode === 'both' ||
                  (item.viewMode === 'logged-in' && authContext.state.user) ||
                  (item.viewMode === 'logged-out' && !authContext.state.user)
                ) {
                  return (
                    <Surface keepParentMode={true} key={item.key}>
                      <li
                        className="flex flex-row p-2 cursor-pointer surface-hover rounded-sm"
                        onClick={item.onClick}
                      >
                        {item.element}
                      </li>
                    </Surface>
                  );
                }
              })}
            </ul>
          </div>
        </Surface>
      )}
    </div>
  );
}
