import React, { useState, useEffect, useRef, useContext } from 'react';
import { IoPersonCircleOutline } from 'react-icons/io5';
import { IoMenuSharp } from 'react-icons/io5';
import { AuthContext } from '../contexts/Auth';
import { SignUp } from './SignUp';
import { LogIn } from './LogIn_';
import { Link } from 'react-router-dom';

import { useClickOutside } from '../utils/useClickOutside';
import { GlobalModalsContext } from '../contexts/GlobalModals';

function AccountIcon() {
  const [isMenuVisible, setIsMenuVisible] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const authContext = useContext(AuthContext);
  const globalModalsContext = useContext(GlobalModalsContext);

  const toggleMenu = () => {
    setIsMenuVisible(!isMenuVisible);
  };

  useClickOutside(menuRef, () => setIsMenuVisible(false));

  return (
    <div className="relative" ref={menuRef}>
      <button
        className="flex flex-row rounded-full border-2 p-2"
        onClick={toggleMenu}
      >
        <IoMenuSharp />
        <IoPersonCircleOutline />
      </button>
      {isMenuVisible && (
        <div className="absolute right-0 mt-2 w-48 bg-inherit border-2 rounded-xl shadow-2xl">
          <ul className="flex flex-col">
            {authContext.state.isActive ? (
              <>
                <Link to="/profile">
                  <li>
                    <p>{authContext.state.auth.user.username}</p>
                  </li>
                </Link>
                <button
                  className="px-4 py-2 hover:bg-gray-100 cursor-pointer"
                  onClick={() => {
                    setIsMenuVisible(false);
                    authContext.dispatch({ type: 'LOGOUT' });
                  }}
                >
                  <span>Log Out</span>
                </button>
              </>
            ) : (
              <>
                <button
                  className="px-4 py-2 hover:bg-gray-100 cursor-pointer"
                  onClick={() => {
                    setIsMenuVisible(false);
                    globalModalsContext.toggleModal('logIn');
                  }}
                >
                  <span>Log In</span>
                </button>
                <button
                  className="px-4 py-2 hover:bg-gray-100 cursor-pointer"
                  onClick={() => {
                    setIsMenuVisible(false);
                    globalModalsContext.toggleModal('signUp');
                  }}
                >
                  <span>Sign Up</span>
                </button>
              </>
            )}
          </ul>
        </div>
      )}
    </div>
  );
}

export { AccountIcon };
