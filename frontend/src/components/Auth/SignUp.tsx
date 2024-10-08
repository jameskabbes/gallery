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
import { InputState } from '../../types';
import { IoWarning } from 'react-icons/io5';

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
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setError(null);
  }, [
    signUpContext.state.email.value,
    signUpContext.state.password.value,
    signUpContext.state.confirmPassword.value,
  ]);

  useEffect(() => {
    if (loading) {
      setError(null);
    }
  }, [loading]);

  useEffect(() => {
    signUpContext.dispatch({
      type: 'SET_VALID',
      payload:
        signUpContext.state.email.status === 'valid' &&
        signUpContext.state.password.status === 'valid' &&
        signUpContext.state.confirmPassword.status === 'valid',
    });
  }, [
    signUpContext.state.email,
    signUpContext.state.password,
    signUpContext.state.confirmPassword,
  ]);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    if (signUpContext.state.valid) {
      setLoading(true);

      const { data, response } = await callApi<
        ResponseTypesByStatus[keyof ResponseTypesByStatus],
        paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/x-www-form-urlencoded']
      >({
        endpoint: API_ENDPOINT,
        method: API_METHOD,
        body: new URLSearchParams({
          email: signUpContext.state.email.value,
          password: signUpContext.state.password.value,
        }).toString(),
        overwriteHeaders: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      setLoading(false);

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
        setError('Error creating user');
      }
    }
  }

  return (
    <div id="sign-up">
      <div className="flex">
        <div className="flex-1">
          <form onSubmit={handleLogin} className="flex flex-col space-y-2">
            <h2 className="text-center">Sign Up</h2>
            <div>
              <label htmlFor="sign-up-email">Email</label>
              <h4>
                <InputText
                  state={signUpContext.state.email}
                  setState={(state: InputState) => {
                    signUpContext.dispatch({
                      type: 'SET_EMAIL',
                      payload: state,
                    });
                  }}
                  id="sign-up-email"
                  minLength={
                    openapi_schema.components.schemas.UserCreate.properties
                      .email.minLength
                  }
                  maxLength={
                    openapi_schema.components.schemas.UserCreate.properties
                      .email.maxLength
                  }
                  type="email"
                  checkAvailability={true}
                  isAvailable={isEmailAvailable}
                  isValid={isEmailValid}
                />
              </h4>
            </div>
            <div>
              <label htmlFor="sign-up-password">
                <p>Password</p>
              </label>
              <h4>
                <InputText
                  state={signUpContext.state.password}
                  setState={(state: InputState) =>
                    signUpContext.dispatch({
                      type: 'SET_PASSWORD',
                      payload: state,
                    })
                  }
                  id="sign-up-password"
                  minLength={
                    openapi_schema.components.schemas.UserCreate.properties
                      .password.anyOf[0].minLength
                  }
                  maxLength={
                    openapi_schema.components.schemas.UserCreate.properties
                      .password.anyOf[0].maxLength
                  }
                  type="password"
                  checkAvailability={false}
                  isValid={isPasswordValid}
                />
              </h4>
            </div>
            <div>
              <label htmlFor="sign-up-confirmPassword">
                <p>Confirm Password</p>
              </label>
              <h4>
                <InputText
                  state={signUpContext.state.confirmPassword}
                  setState={(state: InputState) =>
                    signUpContext.dispatch({
                      type: 'SET_CONFIRM_PASSWORD',
                      payload: state,
                    })
                  }
                  id="sign-up-confirmPassword"
                  minLength={
                    openapi_schema.components.schemas.UserCreate.properties
                      .password.anyOf[0].minLength
                  }
                  maxLength={
                    openapi_schema.components.schemas.UserCreate.properties
                      .password.anyOf[0].maxLength
                  }
                  type="password"
                  checkAvailability={false}
                  isValid={(confirmPassword: InputState['value']) => {
                    if (signUpContext.state.password.status !== 'valid') {
                      return { valid: false, message: 'Password is invalid' };
                    } else if (
                      signUpContext.state.password.value !== confirmPassword
                    ) {
                      return {
                        valid: false,
                        message: 'Passwords do not match',
                      };
                    } else {
                      return { valid: true };
                    }
                  }}
                />
              </h4>
            </div>
            <div className="mt-8"></div>
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
                !signUpContext.state.valid && 'button-invalid'
              }`}
              type="submit"
              disabled={!signUpContext.state.valid}
            >
              <div className="flex flex-row justify-center items-center p-1">
                <h6 className="mb-0 leading-none">
                  {loading ? (
                    <span className="loader-secondary"></span>
                  ) : (
                    'Sign Up'
                  )}
                </h6>
              </div>
            </button>
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
