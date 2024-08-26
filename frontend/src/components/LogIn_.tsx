import React, { useState, useContext, useEffect } from 'react';
import { AuthContext } from '../contexts/Auth';
import openapi_schema from '../../../openapi_schema.json';

import { InputState } from '../types';
import { InputText } from './Form/InputText';
import { Modal } from './Modal';
import { loginUserFunc } from './User/loginUserFunc';
import { LogInContext } from '../contexts/LogIn_';

function LogIn() {
  const logInContext = useContext(LogInContext);
  const authContext = useContext(AuthContext);

  useEffect(() => {
    logInContext.dispatch({
      type: 'SET_VALID',
      payload:
        logInContext.state.username.status === 'valid' &&
        logInContext.state.password.status === 'valid',
    });
  }, [logInContext.state.username.status, logInContext.state.password.status]);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    if (logInContext.state.valid) {
      let newUser = await loginUserFunc(
        {
          username: logInContext.state.username.value,
          password: logInContext.state.password.value,
        },
        authContext.dispatch
      );
    }
  }

  return (
    <>
      {logInContext.state.isActive && (
        <Modal
          onExit={() =>
            logInContext.dispatch({ type: 'SET_ACTIVE', payload: false })
          }
        >
          <div id="login">
            <form onSubmit={handleLogin} className="flex flex-col space-y-2">
              <h4 className="text-center">Login</h4>
              <InputText
                state={logInContext.state.username}
                setState={(state: InputState) => {
                  logInContext.dispatch({
                    type: 'SET_USERNAME',
                    payload: state,
                  });
                }}
                id="username"
                minLength={1}
                maxLength={
                  openapi_schema.components.schemas.UserCreate.properties
                    .username.maxLength
                }
                type="username"
                placeholder="username"
                checkAvailability={false}
              />
              <InputText
                state={logInContext.state.password}
                setState={(state: InputState) =>
                  logInContext.dispatch({
                    type: 'SET_PASSWORD',
                    payload: state,
                  })
                }
                id="password"
                minLength={1}
                maxLength={
                  openapi_schema.components.schemas.UserCreate.properties
                    .password.maxLength
                }
                type="password"
                placeholder="password"
                checkAvailability={false}
              />
              <button
                className={`${
                  logInContext.state.valid ? 'button-valid' : 'button-invalid'
                }`}
                type="submit"
                disabled={!logInContext.state.valid}
              >
                <p className="flex flex-row justify-center items-center">
                  Login
                </p>
              </button>
            </form>
            {/* <GoogleLogin onSuccess={() => {}}></GoogleLogin> */}
          </div>
        </Modal>
      )}
    </>
  );
}

export { LogIn };
