import React, { useState, useContext, useEffect, useRef } from 'react';
import { paths, operations, components } from '../../openapi_schema';
import { AuthModalType, ExtractResponseTypes } from '../../types';
import { callApi } from '../../utils/api';
import openapi_schema from '../../../../openapi_schema.json';

import { AuthContext } from '../../contexts/Auth';
import { AuthModalsContext } from '../../contexts/AuthModals';
import { LogInWithEmailContext } from '../../contexts/LogInWithEmail';

import { isEmailValid } from '../../services/isEmailValid';
import { ValidatedInputString } from '../Form/ValidatedInputString';
import { ButtonSubmit } from '../Utils/Button';
import { ValidatedInputCheckbox } from '../Form/ValidatedInputCheckbox';
import { postEmailMagicLink } from '../../services/api/postEmailMagicLink';
import { ModalsContext } from '../../contexts/Modals';

function LogInWithEmail() {
  const authContext = useContext(AuthContext);
  const logInWithEmailContext = useContext(LogInWithEmailContext);
  const authModalsContext = useContext(AuthModalsContext);
  const modalsContext = useContext(ModalsContext);
  const [loading, setLoading] = useState<boolean>(false);

  const okayButtonRef = useRef<HTMLButtonElement>(null);

  const key: AuthModalType = 'logInWithEmail';

  useEffect(() => {
    logInWithEmailContext.setValid(
      logInWithEmailContext.email.status === 'valid'
    );
  }, [logInWithEmailContext.email.status]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (logInWithEmailContext.screen) {
      setLoading(true);

      const { status } = await postEmailMagicLink(authContext, {
        email: logInWithEmailContext.email.value,
        stay_signed_in: logInWithEmailContext.staySignedIn.value,
      });

      setLoading(false);
      if (status === 200) {
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
                <ValidatedInputString
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
                  checkValidity={true}
                  showStatus={true}
                  isValid={isEmailValid}
                />
              </section>
              <section className="flex flex-row items-center justify-center space-x-2">
                <ValidatedInputCheckbox
                  state={logInWithEmailContext.staySignedIn}
                  setState={logInWithEmailContext.setStaySignedIn}
                  id="login-with-email-stay-signed-in"
                />
                <label htmlFor="login-with-email-stay-signed-in">
                  Remember Me
                </label>
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
              authModalsContext.activate('logIn');
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
            modalsContext.deleteModal(key);
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
