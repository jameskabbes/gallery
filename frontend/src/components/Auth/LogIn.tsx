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
import { IoPersonAddSharp } from 'react-icons/io5';
import { IoMail } from 'react-icons/io5';
import { useLogInWithGoogle } from './LogInWithGoogle';
import { InputCheckbox } from '../Form/InputCheckbox';
import { Button2, ButtonSubmit } from '../Utils/Button';
import { Loader1, Loader2 } from '../Utils/Loader';

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
        logInContext.password.status === 'valid' &&
        !logInContext.loading
    );
  }, [
    logInContext.username.status,
    logInContext.password.status,
    logInContext.loading,
  ]);

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
          stay_signed_in: logInContext.staySignedIn.value.toString(),
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
          <form onSubmit={handleLogin} className="flex flex-col space-y-6">
            <header>Login</header>
            <fieldset className="flex flex-col space-y-4">
              <section className="space-y-2">
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
              <section className="space-y-2">
                <div className="flex flex-row items-center justify-between">
                  <label htmlFor="login-password">Password</label>
                  <span
                    onClick={() =>
                      authModalsContext.setActiveModalType('logInWithEmail')
                    }
                    className="underline cursor-pointer"
                  >
                    Forgot Password?
                  </span>
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
              <section className="flex flex-row items-center space-x-2">
                <label htmlFor="login-stay-signed-in">Remember Me</label>
                <InputCheckbox
                  state={logInContext.staySignedIn}
                  setState={logInContext.setStaySignedIn}
                  type="checkbox"
                  id="login-stay-signed-in"
                />
              </section>
            </fieldset>

            <div className="h-[2em] flex flex-col justify-center">
              {logInContext.loading ? (
                <div className="flex flex-row justify-center items-center space-x-2">
                  <Loader1 />
                  <span className="mb-0">logging in</span>
                </div>
              ) : logInContext.error ? (
                <div className="flex flex-row justify-center items-center space-x-2">
                  <span className="rounded-full p-1 text-light leading-none bg-error-500">
                    <IoWarning
                      style={{
                        animation: 'scaleUp 0.2s ease-in-out',
                      }}
                    />
                  </span>
                  <span>{logInContext.error}</span>
                </div>
              ) : null}
            </div>

            <ButtonSubmit disabled={!logInContext.valid}>Login</ButtonSubmit>
          </form>
          <div className="flex flex-row items-center space-x-2 my-2">
            <div className="surface flex-1 border-t-[1px]" />
            <p>or</p>
            <div className="surface flex-1 border-t-[1px]" />
          </div>

          <div className="space-y-1">
            <Button2
              className="w-full relative"
              onClick={() => {
                authModalsContext.setActiveModalType('signUp');
              }}
            >
              <h6 className="text-center mb-0 ">Sign Up</h6>
              <IoPersonAddSharp className="absolute left-4 top-1/2 transform -translate-y-1/2" />
            </Button2>

            <Button2
              className="w-full relative"
              onClick={() => {
                authModalsContext.setActiveModalType('logInWithEmail');
              }}
            >
              <h6 className="text-center mb-0 ">Login with email</h6>
              <IoMail className="absolute left-4 top-1/2 transform -translate-y-1/2" />
            </Button2>
            <Button2
              className="w-full relative"
              onClick={() => {
                logInWithGoogle();
              }}
            >
              <h6 className="text-center mb-0 ">Login with Google</h6>
              <img
                src="/google_g_logo.svg"
                alt="google_logo"
                className="absolute left-4 top-1/2 transform -translate-y-1/2"
                style={{ width: '1rem', height: '1rem' }}
              />
            </Button2>
          </div>
        </div>
      </div>
    </div>
  );
}

export { LogIn };
