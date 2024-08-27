import React, { useState, useContext, useEffect } from 'react';
import { ModalsContext } from '../contexts/Modals';
import openapi_schema from '../../../openapi_schema.json';

import { SignUpContext } from '../contexts/SignUp';
import { AuthContext } from '../contexts/Auth';
import { GlobalModalsContext } from '../contexts/GlobalModals';

import { Modal } from './Modal';
import { isUsernameAvailable } from './User/isUsernameAvailable';
import { isUsernameValid } from './User/isUsernameValid';
import { isEmailAvailable } from './User/isEmailAvailable';
import { isEmailValid } from './User/isEmailValid';
import { isPasswordValid } from './User/isPasswordValid';
import { InputText } from './Form/InputText';
import { signUpUserFunc } from './User/signUpUserFunc';
import { InputState } from '../types';

function SignUp() {
  const signUpContext = useContext(SignUpContext);
  const authContext = useContext(AuthContext);
  const globalModalsContext = useContext(GlobalModalsContext);

  useEffect(() => {
    signUpContext.dispatch({
      type: 'SET_VALID',
      payload:
        signUpContext.state.username.status === 'valid' &&
        signUpContext.state.email.status === 'valid' &&
        signUpContext.state.password.status === 'valid' &&
        signUpContext.state.confirmPassword.status === 'valid',
    });
  }, [
    signUpContext.state.username,
    signUpContext.state.email,
    signUpContext.state.password,
    signUpContext.state.confirmPassword,
  ]);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    if (signUpContext.state.valid) {
      let resp = await signUpUserFunc(
        {
          email: signUpContext.state.email.value,
          password: signUpContext.state.password.value,
          username: signUpContext.state.username.value,
        },
        authContext.dispatch
      );
      if (resp) {
        signUpContext.dispatch({ type: 'SET_ACTIVE', payload: false });
      }
    }
  }

  return (
    <Modal
      onExit={() =>
        signUpContext.dispatch({
          type: 'SET_ACTIVE',
          payload: false,
        })
      }
      show={signUpContext.state.isActive}
    >
      <div id="signup">
        <form onSubmit={handleLogin} className="flex flex-col space-y-2">
          <h2 className="text-center">Sign Up</h2>
          <h4>
            <InputText
              state={signUpContext.state.username}
              setState={(state: InputState) => {
                signUpContext.dispatch({
                  type: 'SET_USERNAME',
                  payload: state,
                });
              }}
              id="username"
              minLength={
                openapi_schema.components.schemas.UserCreate.properties.username
                  .minLength
              }
              maxLength={
                openapi_schema.components.schemas.UserCreate.properties.username
                  .maxLength
              }
              type="username"
              placeholder="username"
              checkAvailability={true}
              isAvailable={isUsernameAvailable}
              isValid={isUsernameValid}
            />
          </h4>
          <h4>
            <InputText
              state={signUpContext.state.email}
              setState={(state: InputState) => {
                signUpContext.dispatch({
                  type: 'SET_EMAIL',
                  payload: state,
                });
              }}
              id="email"
              minLength={
                openapi_schema.components.schemas.UserCreate.properties.email
                  .minLength
              }
              maxLength={
                openapi_schema.components.schemas.UserCreate.properties.email
                  .maxLength
              }
              type="email"
              placeholder="email"
              checkAvailability={true}
              isAvailable={isEmailAvailable}
              isValid={isEmailValid}
            />
          </h4>
          <h4>
            <InputText
              state={signUpContext.state.password}
              setState={(state: InputState) =>
                signUpContext.dispatch({
                  type: 'SET_PASSWORD',
                  payload: state,
                })
              }
              id="password"
              minLength={
                openapi_schema.components.schemas.UserCreate.properties.password
                  .minLength
              }
              maxLength={
                openapi_schema.components.schemas.UserCreate.properties.password
                  .maxLength
              }
              type="password"
              placeholder="password"
              checkAvailability={false}
              isValid={isPasswordValid}
            />
          </h4>
          <h4>
            <InputText
              state={signUpContext.state.confirmPassword}
              setState={(state: InputState) =>
                signUpContext.dispatch({
                  type: 'SET_CONFIRM_PASSWORD',
                  payload: state,
                })
              }
              id="confirmPassword"
              minLength={
                openapi_schema.components.schemas.UserCreate.properties.password
                  .minLength
              }
              maxLength={
                openapi_schema.components.schemas.UserCreate.properties.password
                  .maxLength
              }
              type="password"
              placeholder="confirm password"
              checkAvailability={false}
              isValid={(confirmPassword: InputState['value']) => {
                if (signUpContext.state.password.status !== 'valid') {
                  return { valid: false, message: 'Password is invalid' };
                } else if (
                  signUpContext.state.password.value !== confirmPassword
                ) {
                  return { valid: false, message: 'Passwords do not match' };
                } else {
                  return { valid: true };
                }
              }}
            />
          </h4>
          <div className="mt-8"></div>
          <button
            className={`${
              signUpContext.state.valid ? 'button-valid' : 'button-invalid'
            }`}
            type="submit"
            disabled={!signUpContext.state.valid}
          >
            <p className="flex flex-row justify-center items-center">Sign Up</p>
          </button>
        </form>
        {/* <GoogleLogin onSuccess={() => {}}></GoogleLogin> */}
        <div className="flex flex-row justify-center mt-2">
          <h6
            className="cursor-pointer underline mb-0"
            onClick={() => {
              globalModalsContext.toggleModal('logIn');
            }}
          >
            Log In
          </h6>
        </div>
      </div>
    </Modal>
  );
}

export { SignUp };
