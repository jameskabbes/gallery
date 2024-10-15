import React, { useState, useContext, useEffect } from 'react';
import { AuthContext } from '../../contexts/Auth';
import { paths, operations, components } from '../../openapi_schema';
import openapi_schema from '../../../../openapi_schema.json';
import { InputText } from '../Form/InputText';
import { LogInContext } from '../../contexts/LogIn';
import { LogInContext as LogInContextType } from '../../types';
import { ToastContext } from '../../contexts/Toast';
import { AuthModalsContext } from '../../contexts/AuthModals';
import { ExtractResponseTypes } from '../../types';
import { callApi } from '../../utils/Api';
import { IoWarning } from 'react-icons/io5';

import { IoMail } from 'react-icons/io5';
import { useLogInWithGoogle } from './LogInWithGoogle';

const API_ENDPOINT = '/auth/login/password/';
const API_METHOD = 'post';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

type TRequestData =
  paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/x-www-form-urlencoded'];

function LogIn() {
  const logInContext = useContext(LogInContext);
  const authContext = useContext(AuthContext);
  const authModalsContext = useContext(AuthModalsContext);
  const toastContext = useContext(ToastContext);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const { logInWithGoogle } = useLogInWithGoogle();

  useEffect(() => {
    setError(null);
  }, [logInContext.state.username.value, logInContext.state.password.value]);

  useEffect(() => {
    if (loading) {
      setError(null);
    }
  }, [loading]);

  useEffect(() => {
    logInContext.dispatch({
      type: 'SET_VALID',
      payload:
        logInContext.state.username.status === 'valid' &&
        logInContext.state.username.status === 'valid',
    });
  }, [logInContext.state.username.status, logInContext.state.password.status]);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    if (logInContext.state.valid) {
      setLoading(true);

      const { data, response } = await callApi<
        ResponseTypesByStatus[keyof ResponseTypesByStatus],
        TRequestData
      >({
        endpoint: API_ENDPOINT,
        method: API_METHOD,
        body: new URLSearchParams({
          username: logInContext.state.username.value,
          password: logInContext.state.password.value,
        }).toString(),
        overwriteHeaders: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      setLoading(false);

      if (response.status == 200) {
        const apiData = data as ResponseTypesByStatus['200'];
        authContext.updateFromApiResponse(apiData);
        authModalsContext.setActiveModalType(null);
        toastContext.make({
          message: `Welcome ${
            apiData.auth.user.username === null
              ? apiData.auth.user.email
              : apiData.auth.user.username
          }`,
          type: 'success',
        });
      } else if (response.status == 401) {
        const apiData = data as ResponseTypesByStatus['401'];
        setError(apiData.detail);
      } else {
        setError('Could not log in');
      }
    }
  }

  return (
    <div id="login">
      <div className="flex">
        <div className="flex-1">
          <form onSubmit={handleLogin} className="flex flex-col space-y-2">
            <h2 className="text-center">Login</h2>
            <div>
              <label htmlFor="login-username">
                <p>Username or Email</p>
              </label>
              <h4>
                <InputText
                  state={logInContext.state.username}
                  setState={(state: LogInContextType['state']['username']) => {
                    logInContext.dispatch({
                      type: 'SET_USERNAME',
                      payload: state,
                    });
                  }}
                  id="login-username"
                  minLength={1}
                  maxLength={Math.max(
                    openapi_schema.components.schemas.UserCreateAdmin.properties
                      .email.maxLength,
                    openapi_schema.components.schemas.User.properties.username
                      .maxLength
                  )}
                  type="text"
                  checkAvailability={false}
                />
              </h4>
            </div>
            <div>
              <label htmlFor="login-password">
                <p>Password</p>
              </label>
              <h4>
                <InputText
                  state={logInContext.state.password}
                  setState={(state: LogInContextType['state']['password']) =>
                    logInContext.dispatch({
                      type: 'SET_PASSWORD',
                      payload: state,
                    })
                  }
                  id="login-password"
                  minLength={
                    openapi_schema.components.schemas.UserCreateAdmin.properties
                      .password.anyOf[0].minLength
                  }
                  maxLength={
                    openapi_schema.components.schemas.UserCreateAdmin.properties
                      .password.anyOf[0].maxLength
                  }
                  type="password"
                  checkAvailability={false}
                />
              </h4>
            </div>
            {error && (
              <div className="flex flex-row justify-center space-x-2">
                <p className="rounded-full p-1 text-light leading-none bg-error-500">
                  <span>
                    <IoWarning
                      style={{
                        animation: 'scaleUp 0.2s ease-in-out',
                      }}
                    />
                  </span>
                </p>
                <p>{error}</p>
              </div>
            )}

            <button
              className={`button-primary ${
                !logInContext.state.valid && 'button-invalid'
              }`}
              type="submit"
              disabled={!logInContext.state.valid}
            >
              <div className="flex flex-row justify-center items-center p-1">
                <h6 className="mb-0 leading-none">
                  {loading ? (
                    <span className="loader-secondary"></span>
                  ) : (
                    'Login'
                  )}
                </h6>
              </div>
            </button>
          </form>
          <div className="flex flex-row justify-center mt-2">
            <h6
              className="cursor-pointer underline mb-0"
              onClick={() => {
                authModalsContext.setActiveModalType('signUp');
              }}
            >
              Sign Up
            </h6>
          </div>

          <div className="flex flex-row items-center space-x-2 my-2">
            <hr className="flex-1 bg-color" />
            <p>or</p>
            <hr className="flex-1 bg-color" />
          </div>

          <div className="space-y-1">
            <button
              className="button-tertiary w-full relative"
              onClick={() => {
                authModalsContext.setActiveModalType('logInWithEmail');
              }}
            >
              <p className="text-center mb-0 ">Login with email</p>
              <IoMail className="absolute left-4 top-1/2 transform -translate-y-1/2" />
            </button>
            <button
              className="button-tertiary w-full relative"
              onClick={() => {
                logInWithGoogle();
              }}
            >
              <p className="text-center mb-0 ">Login with Google</p>
              <img
                src="/google_g_logo.svg"
                alt="google_logo"
                className="absolute left-4 top-1/2 transform -translate-y-1/2"
                style={{ width: '1rem', height: '1rem' }}
              />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export { LogIn };
