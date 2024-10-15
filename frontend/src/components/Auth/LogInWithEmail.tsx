import React, { useState, useContext, useEffect, useRef } from 'react';
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

  const okayButtonRef = useRef<HTMLButtonElement>(null);

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
      if (response.status === 200) {
        logInWithEmailContext.dispatch({ type: 'SET_SCREEN', payload: 'sent' });
      }
    }
  }

  useEffect(() => {
    if (
      logInWithEmailContext.state.screen === 'sent' &&
      okayButtonRef.current
    ) {
      okayButtonRef.current.focus();
    }
  }, [logInWithEmailContext.state.screen]);

  return (
    <div id="login-with-email" className="flex flex-col">
      {logInWithEmailContext.state.screen === 'email' ? (
        <div className="flex flex-col">
          <form onSubmit={handleSubmit} className="flex flex-col">
            <span className="title">Send Email</span>
            <div className="mt-2">
              <label htmlFor="email">Email</label>
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
            <p className="my-4 text-center">
              If an account with this email exists, we will send a login link to
              your email.
            </p>
            <button type="submit" disabled={!logInWithEmailContext.state.valid}>
              <span className="mb-0 leading-none">
                {loading ? (
                  <span className="loader-secondary"></span>
                ) : (
                  'Send Email'
                )}
              </span>
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
        <form
          className="flex flex-col"
          onSubmit={(e) => {
            e.preventDefault();
            authModalsContext.setActiveModalType(null);
            logInWithEmailContext.dispatch({ type: 'RESET' });
          }}
        >
          <span className="title">Done!</span>
          <p className="text-center my-4">
            Check your inbox for a secure login link.
          </p>
          <button type="submit" ref={okayButtonRef}>
            Okay!
          </button>
        </form>
      ) : null}
    </div>
  );
}

export { LogInWithEmail };
