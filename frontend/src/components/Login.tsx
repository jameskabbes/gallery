import React, { useState, useContext, useEffect } from 'react';
import { ModalsContext } from '../contexts/Modals';
import { AuthContext } from '../contexts/Auth';
import openapi_schema from '../../../openapi_schema.json';

import { InputState } from '../types';
import { InputText } from './Form/InputText';
import { Modal } from './Modal';
import { GoogleLogin } from '@react-oauth/google';
import { loginUserFunc } from './User/loginUserFunc';
import { LoginContext } from '../contexts/Login';

function Login() {
  const loginContext = useContext(LoginContext);
  const modalsContext = useContext(ModalsContext);
  const authContext = useContext(AuthContext);

  useEffect(() => {
    loginContext.dispatch({
      type: 'SET_VALID',
      payload:
        loginContext.state.username.status === 'valid' &&
        loginContext.state.password.status === 'valid',
    });
  }, [loginContext.state.username.status, loginContext.state.password.status]);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    if (loginContext.state.valid) {
      let newUser = await loginUserFunc(
        {
          username: loginContext.state.username.value,
          password: loginContext.state.password.value,
        },
        authContext.dispatch
      );
      if (newUser) {
        modalsContext.dispatch({ type: 'POP' });
      }
    }
  }

  return (
    <Modal>
      <div id="login">
        {/* modes */}
        <form onSubmit={handleLogin} className="flex flex-col space-y-2">
          <h4 className="text-center">Login</h4>
          <InputText
            state={loginContext.state.username}
            setState={(state: InputState) =>
              loginContext.dispatch({ type: 'SET_USERNAME', payload: state })
            }
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
          <InputText
            state={loginContext.state.password}
            setState={(state: InputState) =>
              loginContext.dispatch({ type: 'SET_PASSWORD', payload: state })
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
          <button
            className={`${
              loginContext.state.valid ? 'button-valid' : 'button-invalid'
            }`}
            type="submit"
            disabled={!loginContext.state.valid}
          >
            <p className="flex flex-row justify-center items-center">Login</p>
          </button>
        </form>
        {/* <GoogleLogin onSuccess={() => {}}></GoogleLogin> */}
      </div>
    </Modal>
  );
}

export { Login };
