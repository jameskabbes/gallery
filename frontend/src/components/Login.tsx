import React, { useState, useContext, useEffect } from 'react';
import { ModalsContext } from '../contexts/Modals';
import { callApiBase, callBackendApi } from '../utils/Api';
import { paths, operations, components } from '../openapi_schema';
import { ExtractResponseTypes } from '../types';
import openapi_schema from '../../../openapi_schema.json';

import { InputText, InputState, defaultInputState } from './Form/InputText';

import { Modal } from './Modal';
import { GoogleLogin } from '@react-oauth/google';

const API_PATH = '/token/';
const API_METHOD = 'post';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_PATH][typeof API_METHOD]['responses']
>;

function Login() {
  const [username, setUsername] = useState<InputState>({
    ...defaultInputState,
  });
  const [password, setPassword] = useState<InputState>({
    ...defaultInputState,
  });
  const [valid, setValid] = useState(false);

  useEffect(() => {
    setValid(username.status === 'valid' && password.status === 'valid');
  }, [username.status, password.status]);

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
          username: username.value,
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
          <InputText
            state={username}
            setState={setUsername}
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
            state={password}
            setState={setPassword}
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
            className={`${valid ? 'button-valid' : 'button-invalid'}`}
            type="submit"
            disabled={!valid}
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
