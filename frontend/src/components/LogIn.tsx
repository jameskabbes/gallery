import React, { useState, useContext, useEffect } from 'react';
import { AuthContext } from '../contexts/Auth';
import openapi_schema from '../../../openapi_schema.json';

import { InputState } from '../types';
import { InputText } from './Form/InputText';
import { Modal } from './Modal';
import { logInUserFunc } from './User/logInUserFunc';
import { LogInContext } from '../contexts/LogIn';

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
      let resp = await logInUserFunc(
        {
          username: logInContext.state.username.value,
          password: logInContext.state.password.value,
        },
        authContext.dispatch
      );
      if (resp) {
        logInContext.dispatch({ type: 'SET_ACTIVE', payload: false });
      }
    }
  }

  return (
    <Modal
      onExit={() =>
        logInContext.dispatch({ type: 'SET_ACTIVE', payload: false })
      }
      show={logInContext.state.isActive}
    >
      <div id="login" className="">
        <form onSubmit={handleLogin} className="flex flex-col space-y-2">
          <h2 className="text-center">Login</h2>
          <h4>
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
                openapi_schema.components.schemas.UserCreate.properties.username
                  .maxLength
              }
              type="username"
              placeholder="username"
              checkAvailability={false}
            />
          </h4>
          <h4>
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
                openapi_schema.components.schemas.UserCreate.properties.password
                  .maxLength
              }
              type="password"
              placeholder="password"
              checkAvailability={false}
            />
          </h4>
          <div className="mt-8"></div>
          <button
            className={`${
              logInContext.state.valid ? 'button-valid' : 'button-invalid'
            }`}
            type="submit"
            disabled={!logInContext.state.valid}
          >
            <p className="flex flex-row justify-center items-center">Login</p>
          </button>
        </form>
        {/* <GoogleLogin onSuccess={() => {}}></GoogleLogin> */}
      </div>
    </Modal>
  );
}

export { LogIn };
