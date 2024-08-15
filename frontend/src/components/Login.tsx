import React, { useState, useContext, useEffect } from 'react';
import { ModalsContext } from '../contexts/Modals';
import { callApiBase, callBackendApi } from '../utils/Api';
import validator from 'validator';
import { paths, operations, components } from '../openapi_schema';
import { ExtractResponseTypes } from '../types';
import { Status as InputStatus, CheckOrX } from './Form/CheckOrX';

import { isEmailValid } from './User/isEmailValid';
import { isPasswordValid } from './User/isPasswordValid';

import { toast } from 'react-toastify';
import { toastTemplate } from './Toast';

import { Modal } from './Modal';
import { GoogleLogin } from '@react-oauth/google';

const API_PATH = '/token/';
const API_METHOD = 'post';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_PATH][typeof API_METHOD]['responses']
>;

interface InputFields {
  value: string;
  status: InputStatus;
  error: string | null;
}

const defaultInputFields: InputFields = {
  value: '',
  status: 'invalid',
  error: null,
};

function Login() {
  const [email, setEmail] = useState<InputFields>({ ...defaultInputFields });
  const [password, setPassword] = useState<InputFields>({
    ...defaultInputFields,
  });
  const [valid, setValid] = useState(false);

  useEffect(() => {
    const { valid, message } = isEmailValid(email.value);
    setEmail((prevState) => ({
      ...prevState,
      status: valid ? 'valid' : 'invalid',
      error: message,
    }));
  }, [email.value]);
  useEffect(() => {
    const { valid, message } = isPasswordValid(password.value);
    setPassword((prevState) => ({
      ...prevState,
      status: password.value.length > 0 ? 'valid' : 'invalid',
    }));
  }, [password.value]);
  useEffect(() => {
    setValid(email.status === 'valid' && password.status === 'valid');
  }, [email.status, password.status]);

  async function handleLogin(e: React.FormEvent) {
    const API_ENDPOINT = '/token/';
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
          <h4 className="text-center">Login</h4>
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
          <button
            className={`${valid ? 'button-valid' : 'button-invalid'}`}
            type="submit"
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
