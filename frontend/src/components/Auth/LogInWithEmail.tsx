import React, { useState, useContext, useEffect } from 'react';
import { paths, operations, components } from '../../openapi_schema';
import { ExtractResponseTypes } from '../../types';
import { callApi } from '../../utils/Api';
import openapi_schema from '../../../../openapi_schema.json';

import { AuthModalsContext } from '../../contexts/AuthModals';
import { LogInWithEmailContext } from '../../contexts/LogInWithEmail';

import { LogInWithEmailContext as LogInWithEmailContextType } from '../../types';

import { isEmailValid } from '../../services/api/isEmailValid';
import { InputText } from '../Form/InputText';
import { InputState } from '../../types';

const API_ENDPOINT = '/auth/login/email-magic-link/';
const API_METHOD = 'post';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

type TRequestData =
  paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json'];

function LogInWithEmail() {
  const logInWithEmailContext = useContext(LogInWithEmailContext);
  const authModalsContext = useContext(AuthModalsContext);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    logInWithEmailContext.dispatch({
      type: 'SET_VALID',
      payload: logInWithEmailContext.state.email.status === 'valid',
    });
  }, [logInWithEmailContext.state.email.status]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (logInWithEmailContext.state.screen) {
      setLoading(true);

      const { data, response } = await callApi<
        ResponseTypesByStatus[keyof ResponseTypesByStatus],
        TRequestData
      >({
        endpoint: API_ENDPOINT,
        method: API_METHOD,
        data: { email: logInWithEmailContext.state.email.value },
      });

      setLoading(false);

      console.log(data);
      console.log(response);

      if (response.status === 200) {
        logInWithEmailContext.dispatch({ type: 'SET_SCREEN', payload: 'sent' });
      }
    }
  }

  return (
    <div id="login-with-email" className="flex flex-col">
      {logInWithEmailContext.state.screen === 'email' ? (
        <div className="flex flex-col">
          <form onSubmit={handleSubmit} className="flex flex-col">
            <h2 className="text-center">Send Email</h2>
            <div className="mt-2">
              <label htmlFor="email">
                <p>Email</p>
              </label>
              <h4>
                <InputText
                  state={logInWithEmailContext.state.email}
                  setState={(
                    state: LogInWithEmailContextType['state']['email']
                  ) => {
                    logInWithEmailContext.dispatch({
                      type: 'SET_EMAIL',
                      payload: state,
                    });
                  }}
                  id="login-with-email-email"
                  minLength={
                    openapi_schema.components.schemas.User.properties.email
                      .minLength
                  }
                  maxLength={
                    openapi_schema.components.schemas.User.properties.email
                      .maxLength
                  }
                  type="email"
                  isValid={isEmailValid}
                />
              </h4>
            </div>
            <p>
              If an account with this email exists, we will send a login link to
              your email.
            </p>
            <button
              className={`button-primary ${
                !logInWithEmailContext.state.valid && 'button-invalid'
              }`}
              type="submit"
              disabled={!logInWithEmailContext.state.valid}
            >
              <h6 className="mb-0 leading-none p-2">
                {loading ? (
                  <span className="loader-secondary"></span>
                ) : (
                  'Send Email'
                )}
              </h6>
            </button>
          </form>
          <h6
            className="cursor-pointer underline text-center mt-2"
            onClick={() => {
              authModalsContext.setActiveModalType('logIn');
            }}
          >
            Back to Login
          </h6>
        </div>
      ) : logInWithEmailContext.state.screen === 'sent' ? (
        <div className="flex flex-col">
          <h2 className="text-center">Sent!</h2>
          <p className="text-center">
            Check your inbox for a secure login link.
          </p>
          <button
            className="button-primary mt-4"
            onClick={() => {
              authModalsContext.setActiveModalType(null);
            }}
          >
            Okay!
          </button>
        </div>
      ) : null}
    </div>
  );
}

export { LogInWithEmail };
