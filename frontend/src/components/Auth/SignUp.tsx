import React, { useState, useContext, useEffect } from 'react';
import { paths, operations, components } from '../../openapi_schema';
import { ExtractResponseTypes } from '../../types';
import { callApi } from '../../utils/Api';

import openapi_schema from '../../../../openapi_schema.json';

import { SignUpContext } from '../../contexts/SignUp';
import { AuthContext } from '../../contexts/Auth';
import { AuthModalsContext } from '../../contexts/AuthModals';
import { ToastContext } from '../../contexts/Toast';

import { isEmailValid } from '../../services/api/isEmailValid';
import { isEmailAvailable } from '../../services/api/isEmailAvailable';
import { isPasswordValid } from '../../services/api/isPasswordValid';
import { InputText } from '../Form/InputText';
import { IoWarning } from 'react-icons/io5';
import { ButtonSubmit } from '../Utils/Button';
import { Loader3 } from '../Utils/Loader';

const API_ENDPOINT = '/auth/signup/';
const API_METHOD = 'post';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

function SignUp() {
  const signUpContext = useContext(SignUpContext);
  const authContext = useContext(AuthContext);
  const authModalsContext = useContext(AuthModalsContext);
  const toastContext = useContext(ToastContext);

  useEffect(() => {
    signUpContext.setError(null);
  }, [
    signUpContext.email.value,
    signUpContext.password.value,
    signUpContext.confirmPassword.value,
  ]);

  useEffect(() => {
    if (signUpContext.loading) {
      signUpContext.setError(null);
    }
  }, [signUpContext.loading]);

  useEffect(() => {
    signUpContext.setValid(
      signUpContext.email.status === 'valid' &&
        signUpContext.password.status === 'valid' &&
        signUpContext.confirmPassword.status === 'valid'
    );
  }, [
    signUpContext.email,
    signUpContext.password,
    signUpContext.confirmPassword,
  ]);

  useEffect(() => {
    if (signUpContext.password.status !== 'valid') {
      signUpContext.setConfirmPassword((prev) => ({
        ...prev,
        status: 'invalid',
        message: 'Password is invalid',
      }));
    } else if (
      signUpContext.password.value !== signUpContext.confirmPassword.value
    ) {
      signUpContext.setConfirmPassword((prev) => ({
        ...prev,
        status: 'invalid',
        message: 'Passwords do not match',
      }));
    } else {
      signUpContext.setConfirmPassword((prev) => ({
        ...prev,
        status: 'valid',
      }));
    }
  }, [signUpContext.confirmPassword.value, signUpContext.password]);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    if (signUpContext.valid) {
      signUpContext.setLoading(true);

      const { data, response } = await callApi<
        ResponseTypesByStatus[keyof ResponseTypesByStatus],
        paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/x-www-form-urlencoded']
      >({
        endpoint: API_ENDPOINT,
        method: API_METHOD,
        body: new URLSearchParams({
          email: signUpContext.email.value,
          password: signUpContext.password.value,
        }).toString(),
        overwriteHeaders: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      signUpContext.setLoading(false);

      if (response.status === 200) {
        const apiData = data as ResponseTypesByStatus['200'];
        authContext.updateFromApiResponse(apiData);
        toastContext.make({
          message: 'Created new user: ' + apiData.auth.user.username,
          type: 'success',
        });
        authModalsContext.setActiveModalType(null);
      } else {
        console.error('Error creating user:', response.status, data);
        signUpContext.setError('Error creating user');
      }
    }
  }

  return (
    <div id="sign-up">
      <div className="flex">
        <div className="flex-1">
          <form onSubmit={handleLogin} className="flex flex-col space-y-2">
            <header>Sign Up</header>
            <section>
              <label htmlFor="sign-up-email">Email</label>
              <InputText
                state={signUpContext.email}
                setState={signUpContext.setEmail}
                id="sign-up-email"
                minLength={
                  openapi_schema.components.schemas.UserCreateAdmin.properties
                    .email.minLength
                }
                maxLength={
                  openapi_schema.components.schemas.UserCreateAdmin.properties
                    .email.maxLength
                }
                type="email"
                checkAvailability={true}
                isAvailable={isEmailAvailable}
                isValid={isEmailValid}
              />
            </section>
            <section>
              <label htmlFor="sign-up-password">Password</label>
              <InputText
                state={signUpContext.password}
                setState={signUpContext.setPassword}
                id="sign-up-password"
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
                isValid={isPasswordValid}
              />
            </section>
            <section>
              <label htmlFor="sign-up-confirmPassword">Confirm Password</label>
              <InputText
                state={signUpContext.confirmPassword}
                setState={signUpContext.setConfirmPassword}
                id="sign-up-confirmPassword"
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
            <section className="mt-8">
              {signUpContext.error && (
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
                  <p>{signUpContext.error}</p>
                </div>
              )}
            </section>
            <ButtonSubmit disabled={!signUpContext.valid}>
              {signUpContext.loading ? (
                <Loader3 />
              ) : (
                <span className="leading-none">Login</span>
              )}
            </ButtonSubmit>
          </form>
          {/* <GoogleLogin onSuccess={() => {}}></GoogleLogin> */}
          <div className="flex flex-row justify-center mt-2">
            <h6
              className="cursor-pointer underline mb-0"
              onClick={() => {
                authModalsContext.setActiveModalType('logIn');
              }}
            >
              Log In
            </h6>
          </div>
        </div>
      </div>
    </div>
  );
}

export { SignUp };
