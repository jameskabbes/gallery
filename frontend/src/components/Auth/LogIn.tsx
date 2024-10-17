import React, { useState, useContext, useEffect } from 'react';
import { AuthContext } from '../../contexts/Auth';
import { paths, operations, components } from '../../openapi_schema';
import openapi_schema from '../../../../openapi_schema.json';
import { InputText } from '../Form/InputText';
import { LogInContext } from '../../contexts/LogIn';
import { ToastContext } from '../../contexts/Toast';
import { AuthModalsContext } from '../../contexts/AuthModals';
import { ExtractResponseTypes } from '../../types';
import { callApi } from '../../utils/Api';
import { IoWarning } from 'react-icons/io5';
import { InputState } from '../../types';
import { IoPersonAddSharp } from 'react-icons/io5';
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
  const { logInWithGoogle } = useLogInWithGoogle();

  useEffect(() => {
    logInContext.setError(null);
  }, [logInContext.username.value, logInContext.password.value]);

  useEffect(() => {
    if (logInContext.loading) {
      logInContext.setError(null);
    }
  }, [logInContext.loading]);

  useEffect(() => {
    logInContext.setValid(
      logInContext.username.status === 'valid' &&
        logInContext.password.status === 'valid'
    );
  }, [logInContext.username.status, logInContext.password.status]);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    if (logInContext.valid) {
      logInContext.setLoading(true);

      const { data, response } = await callApi<
        ResponseTypesByStatus[keyof ResponseTypesByStatus],
        TRequestData
      >({
        endpoint: API_ENDPOINT,
        method: API_METHOD,
        body: new URLSearchParams({
          username: logInContext.username.value,
          password: logInContext.password.value,
          stay_signed_in: logInContext.staySignedIn.toString(),
        }).toString(),
        overwriteHeaders: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      logInContext.setLoading(false);

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
        logInContext.setError(apiData.detail);
      } else {
        logInContext.setError('Could not log in');
      }
    }
  }

  return (
    <div id="login">
      <div className="flex">
        <div className="flex-1">
          <form onSubmit={handleLogin} className="flex flex-col space-y-2">
            <header>Login</header>
            <section>
              <label htmlFor="login-username">Username or Email</label>
              <InputText
                state={logInContext.username}
                setState={logInContext.setUsername}
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
            </section>
            <section>
              <div className="flex flex-row justify-between items-center">
                <label htmlFor="login-password">Password</label>
              </div>
              <InputText
                state={logInContext.password}
                setState={logInContext.setPassword}
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
            </section>

            <div className="flex flex-row items-center space-x-2">
              <label htmlFor="login-stay-signed-in">Stay signed in</label>
              <input
                type="checkbox"
                id="login-stay-signed-in"
                checked={logInContext.staySignedIn}
                onChange={(e) => logInContext.setStaySignedIn(e.target.checked)}
              />
            </div>

            {logInContext.error && (
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
                <p>{logInContext.error}</p>
              </div>
            )}
            <button type="submit" disabled={!logInContext.valid}>
              <span className="leading-none mb-0">
                {logInContext.loading ? (
                  <span className="loader-secondary"></span>
                ) : (
                  'Login'
                )}
              </span>
            </button>
          </form>
          <div className="flex flex-row items-center space-x-2 my-2">
            <hr className="flex-1 bg-color" />
            <p>or</p>
            <hr className="flex-1 bg-color" />
          </div>

          <div className="space-y-1">
            <button
              className="button-secondary w-full relative"
              onClick={() => {
                authModalsContext.setActiveModalType('signUp');
              }}
            >
              <p className="text-center mb-0 ">Sign Up</p>
              <IoPersonAddSharp className="absolute left-4 top-1/2 transform -translate-y-1/2" />
            </button>

            <button
              className="button-secondary w-full relative"
              onClick={() => {
                authModalsContext.setActiveModalType('logInWithEmail');
              }}
            >
              <p className="text-center mb-0 ">Login with email</p>
              <IoMail className="absolute left-4 top-1/2 transform -translate-y-1/2" />
            </button>
            <button
              className="button-secondary w-full relative"
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
