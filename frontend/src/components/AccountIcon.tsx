import React, { useState, useEffect, useRef, useContext } from 'react';
import { IoPersonCircleOutline } from 'react-icons/io5';
import { IoMenuSharp } from 'react-icons/io5';
import { ModalsContext } from '../contexts/Modals';
import { AuthContext } from '../contexts/Auth';
import { SignUp } from './SignUp';
import { Login } from './Login';
import { Link } from 'react-router-dom';

import { useClickOutside } from '../utils/useClickOutside';

function AccountIcon() {
  const [isMenuVisible, setIsMenuVisible] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const modalsContext = useContext(ModalsContext);
  const authContext = useContext(AuthContext);

  const toggleMenu = () => {
    setIsMenuVisible(!isMenuVisible);
  };

  useClickOutside(menuRef, () => setIsMenuVisible(false));

  useEffect(() => {
    console.log('auth context state');
    console.log(authContext.state);
  }, [authContext.state]);

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
                    modalsContext.dispatch({
                      type: 'PUSH',
                      payload: <Login />,
                    });
                  }}
                >
                  <span>Log In</span>
                </button>
                <button
                  className="px-4 py-2 hover:bg-gray-100 cursor-pointer"
                  onClick={() => {
                    setIsMenuVisible(false);
                    modalsContext.dispatch({
                      type: 'PUSH',
                      payload: <SignUp />,
                    });
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
