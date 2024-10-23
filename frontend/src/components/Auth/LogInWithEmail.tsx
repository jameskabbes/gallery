import React, { useState, useContext, useEffect, useRef } from 'react';
import { paths, operations, components } from '../../openapi_schema';
import { ExtractResponseTypes } from '../../types';
import { callApi } from '../../utils/Api';
import openapi_schema from '../../../../openapi_schema.json';

import { AuthModalsContext } from '../../contexts/AuthModals';
import { LogInWithEmailContext } from '../../contexts/LogInWithEmail';

import { isEmailValid } from '../../services/api/isEmailValid';
import { InputText } from '../Form/InputText';
import { ButtonSubmit } from '../Utils/Button';

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
    logInWithEmailContext.setValid(
      logInWithEmailContext.email.status === 'valid'
    );
  }, [logInWithEmailContext.email.status]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (logInWithEmailContext.screen) {
      setLoading(true);

      const { data, response } = await callApi<
        ResponseTypesByStatus[keyof ResponseTypesByStatus],
        TRequestData
      >({
        endpoint: API_ENDPOINT,
        method: API_METHOD,
        data: { email: logInWithEmailContext.email.value },
      });

      setLoading(false);
      if (response.status === 200) {
        logInWithEmailContext.setScreen('sent');
      }
    }
  }

  useEffect(() => {
    if (logInWithEmailContext.screen === 'sent' && okayButtonRef.current) {
      okayButtonRef.current.focus();
    }
  }, [logInWithEmailContext.screen]);

  return (
    <div id="login-with-email" className="flex flex-col">
      {logInWithEmailContext.screen === 'email' ? (
        <div className="flex flex-col">
          <form onSubmit={handleSubmit} className="flex flex-col space-y-6">
            <header>Send Email</header>
            <fieldset className="flex flex-col space-y-6">
              <section className="space-y-2">
                <label htmlFor="email">Email</label>
                <InputText
                  state={logInWithEmailContext.email}
                  setState={logInWithEmailContext.setEmail}
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
              </section>
            </fieldset>
            <span className="text-center mx-10">
              If an account with this email exists, we will send a login link to
              your email.
            </span>
            <ButtonSubmit disabled={!logInWithEmailContext.valid}>
              Send Email
            </ButtonSubmit>
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
      ) : logInWithEmailContext.screen === 'sent' ? (
        <form
          className="flex flex-col"
          onSubmit={(e) => {
            e.preventDefault();
            authModalsContext.setActiveModalType(null);
            logInWithEmailContext.setScreen('email');
          }}
        >
          <header>Done!</header>
          <section>
            <span></span>
            <p className="text-center my-4">
              Check your inbox for a secure login link.
            </p>
          </section>
          <ButtonSubmit ref={okayButtonRef}>
            <span className="leading-none mb-0">Okay!</span>
          </ButtonSubmit>
        </form>
      ) : null}
    </div>
  );
}

export { LogInWithEmail };
