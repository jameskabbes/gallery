import React, { useState, useContext, useEffect } from 'react';
import { ModalsContext } from '../contexts/Modals';
import { callApiBase, callBackendApi } from '../utils/Api';
import { paths, operations, components } from '../openapi_schema';
import { ExtractResponseTypes } from '../types';
import { Status as InputStatus, CheckOrX } from './Form/CheckOrX';
import openapi_schema from '../../../openapi_schema.json';

import { Modal } from './Modal';
import { isUsernameAvailable } from './User/isUsernameAvailable';
import { isUsernameValid } from './User/isUsernameValid';
import { isEmailAvailable } from './User/isEmailAvailable';
import { isEmailValid } from './User/isEmailValid';
import { isPasswordValid } from './User/isPasswordValid';
import { InputState, InputText, defaultInputState } from './Form/InputText';
import { createUserFunc } from './User/createUserFunc';

function SignUp() {
  // value, valid, loading, errorMessage

  const [username, setUsername] = useState<InputState>({
    ...defaultInputState,
  });
  const [email, setEmail] = useState<InputState>({ ...defaultInputState });
  const [password, setPassword] = useState<InputState>({
    ...defaultInputState,
  });
  const [confirmPassword, setConfirmPassword] = useState<InputState>({
    ...defaultInputState,
  });

  const [valid, setValid] = useState<boolean>(false);
  useEffect(() => {
    setValid(
      username.status === 'valid' &&
        email.status === 'valid' &&
        password.status === 'valid' &&
        confirmPassword.status === 'valid'
    );
  }, [username.status, email.status, password.status, confirmPassword.status]);

  let modalContext = useContext(ModalsContext);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    let newUser = await createUserFunc({
      email: email.value,
      password: password.value,
      username: username.value,
    });
    console.log(newUser);
    modalContext.dispatch({ type: 'POP' });
  }

  return (
    <Modal>
      <div id="login">
        {/* modes */}
        <form onSubmit={handleLogin} className="flex flex-col space-y-2">
          <h4 className="text-center">Sign Up</h4>
          <InputText
            state={username}
            setState={setUsername}
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

          <InputText
            state={email}
            setState={setEmail}
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
          <InputText
            state={password}
            setState={setPassword}
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
          <InputText
            state={confirmPassword}
            setState={setConfirmPassword}
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
              if (password.status !== 'valid') {
                return { valid: false, message: 'Password is invalid' };
              } else if (password.value !== confirmPassword) {
                return { valid: false, message: 'Passwords do not match' };
              } else {
                return { valid: true };
              }
            }}
          />

          <button
            className={`${valid ? 'button-valid' : 'button-invalid'}`}
            type="submit"
            disabled={!valid}
          >
            <p className="flex flex-row justify-center items-center">Sign Up</p>
          </button>
        </form>
        {/* <GoogleLogin onSuccess={() => {}}></GoogleLogin> */}
      </div>
    </Modal>
  );
}

export { SignUp };
