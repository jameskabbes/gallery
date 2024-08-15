import React, { useState, useContext, useEffect } from 'react';
import { ModalsContext } from '../contexts/Modals';
import { callApiBase, callBackendApi } from '../utils/Api';
import validator from 'validator';
import { paths, operations, components } from '../openapi_schema';
import { ExtractResponseTypes } from '../types';
import { Status as InputStatus, CheckOrX } from './Form/CheckOrX';

import { Modal } from './Modal';
import { isUsernameAvailable } from './User/isUsernameAvailable';
import { isUsernameValid } from './User/isUsernameValid';
import { isEmailAvailable } from './User/isEmailAvailable';
import { isEmailValid } from './User/isEmailValid';
import { isPasswordValid } from './User/isPasswordValid';

interface InputFields {
  value: string;
  status: InputStatus;
  error: string | null;
}

const debounceTimeouts = {
  username: null,
  email: null,
};

const defaultInputFields: InputFields = {
  value: '',
  status: 'invalid',
  error: null,
};

function SignUp() {
  // value, valid, loading, errorMessage

  const [username, setUsername] = useState<InputFields>({
    ...defaultInputFields,
  });
  const [email, setEmail] = useState<InputFields>({ ...defaultInputFields });
  const [password, setPassword] = useState<InputFields>({
    ...defaultInputFields,
  });
  const [confirmPassword, setConfirmPassword] = useState<InputFields>({
    ...defaultInputFields,
  });

  const [valid, setValid] = useState<boolean>(false);

  function verifyPipeline(
    isValidFunc,
    isAvailableFunc,
    item,
    setItem,
    itemKey
  ) {
    const { valid, message } = isValidFunc(item.value);

    if (!valid) {
      setItem((prevState) => ({
        ...prevState,
        status: 'invalid',
        error: message,
      }));
      return;
    }

    setItem((prevState) => ({
      ...prevState,
      status: 'loading',
    }));

    async function callApi() {
      let available = await isAvailableFunc(item.value);
      setItem((prevState) => ({
        ...prevState,
        status: available ? 'valid' : 'invalid',
        error: available ? null : `${itemKey} not available`,
      }));
    }
    if (debounceTimeouts[itemKey]) {
      clearTimeout(debounceTimeouts[itemKey]);
    }

    debounceTimeouts[itemKey] = setTimeout(() => {
      callApi();
    }, 200);

    return () => {
      clearTimeout(debounceTimeouts[itemKey]);
    };
  }

  useEffect(() => {
    return verifyPipeline(
      isUsernameValid,
      isUsernameAvailable,
      username,
      setUsername,
      'username'
    );
  }, [username.value]);

  useEffect(() => {
    return verifyPipeline(
      isEmailValid,
      isEmailAvailable,
      email,
      setEmail,
      'email'
    );
  }, [email.value]);

  useEffect(() => {
    let { valid, message } = isPasswordValid(password.value);
    setPassword((prevState) => ({
      ...prevState,
      status: valid ? 'valid' : 'invalid',
      error: message,
    }));
  }, [password.value]);

  useEffect(() => {
    if (password.status !== 'valid') {
      setConfirmPassword((prevState) => ({
        ...prevState,
        status: 'invalid',
        error: 'Password is invalid',
      }));
    } else {
      if (password.value !== confirmPassword.value) {
        setConfirmPassword((prevState) => ({
          ...prevState,
          status: 'invalid',
          error: 'Passwords do not match',
        }));
      } else {
        setConfirmPassword((prevState) => ({
          ...prevState,
          status: 'valid',
          error: null,
        }));
      }
    }
  }, [password.value, confirmPassword.value]);

  useEffect(() => {
    setValid(
      username.status === 'valid' &&
        email.status === 'valid' &&
        password.status === 'valid' &&
        confirmPassword.status === 'valid'
    );
  }, [username.status, email.status, password.status, confirmPassword.status]);

  async function handleLogin(e: React.FormEvent) {
    const API_ENDPOINT = '/users/';
    const API_METHOD = 'post';

    type ResponseTypesByStatus = ExtractResponseTypes<
      paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
    >;

    e.preventDefault();
    // Simple validation
    if (valid) {
      const { data, response } = await callBackendApi<
        ResponseTypesByStatus[keyof ResponseTypesByStatus],
        paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
      >({
        endpoint: API_ENDPOINT,
        method: API_METHOD,
        data: {
          email: email.value,
          password: password.value,
          username: username.value,
        },
      });
      console.log(data);
      console.log(response);
    }
  }

  return (
    <Modal>
      <div id="login">
        {/* modes */}
        <form onSubmit={handleLogin} className="flex flex-col space-y-2">
          <h4 className="text-center">Sign Up</h4>
          <div className="flex flex-row items-center space-x-2">
            <input
              className="text-input"
              type="username"
              id="username"
              value={username.value}
              placeholder="username"
              onChange={(e) => {
                let newUsername: InputFields['value'] = e.target.value;
                setUsername((prevState) => ({
                  ...prevState,
                  value: newUsername,
                }));
              }}
              required
              formNoValidate
            />
            <span title={username.error || ''}>
              <CheckOrX status={username.status} />
            </span>
          </div>
          <div className="flex flex-row items-center space-x-2">
            <input
              className="text-input"
              type="email"
              id="email"
              value={email.value}
              placeholder="email"
              onChange={(e) => {
                let newEmail: InputFields['value'] = e.target.value;
                setEmail((prevState) => ({
                  ...prevState,
                  value: newEmail,
                }));
              }}
              required
              formNoValidate
            />

            <span title={email.error || ''}>
              <CheckOrX status={email.status} />
            </span>
          </div>
          <div className="flex flex-row items-center space-x-2">
            <input
              className="text-input"
              type="password"
              id="password"
              value={password.value}
              placeholder="password"
              onChange={(e) => {
                let newPassword: InputFields['value'] = e.target.value;
                setPassword((prevState) => ({
                  ...prevState,
                  value: newPassword,
                }));
              }}
              required
              formNoValidate
            />

            <span title={password.error || ''}>
              <CheckOrX status={password.status} />
            </span>
          </div>
          <div className="flex flex-row items-center space-x-2">
            <input
              className="text-input"
              type="password"
              id="confirmPassword"
              value={confirmPassword.value}
              placeholder="confirm password"
              onChange={(e) => {
                let newConfirmPassword: InputFields['value'] = e.target.value;
                setConfirmPassword((prevState) => ({
                  ...prevState,
                  value: newConfirmPassword,
                }));
              }}
              required
              formNoValidate
            />

            <span title={confirmPassword.error || ''}>
              <CheckOrX status={confirmPassword.status} />
            </span>
          </div>

          <button
            className={`${valid ? 'button-valid' : 'button-invalid'}`}
            type="submit"
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
