import React, { useState, useContext, useEffect } from 'react';
import { ModalsContext } from '../../contexts/Modals';
import { paths, operations, components } from '../../openapi_schema';
import { ExtractResponseTypes } from '../../types';
import { callApi } from '../../utils/Api';
import openapi_schema from '../../../../openapi_schema.json';

import { GlobalModalsContext } from '../../contexts/GlobalModals';
import { LogInWithEmailContext } from '../../contexts/LogInWithEmail';

import { Modal } from '../Modal/Modal';
import { isEmailValid } from '../User/isEmailValid';
import { InputText } from '../Form/InputText';
import { InputState } from '../../types';

const API_ENDPOINT = '/login-with-email/';
const API_METHOD = 'post';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

function LogInWithEmail() {
  const logInWithEmailContext = useContext(LogInWithEmailContext);
  const globalModalsContext = useContext(GlobalModalsContext);
  const [loading, setLoading] = useState<boolean>(false);
  const [sent, setSent] = useState<boolean>(false);

  useEffect(() => {
    logInWithEmailContext.dispatch({
      type: 'SET_VALID',
      payload: logInWithEmailContext.state.email.status === 'valid',
    });
  }, [logInWithEmailContext.state.email.status]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (logInWithEmailContext.state.valid) {
      setLoading(true);

      const { data, response } = await callApi<
        ResponseTypesByStatus[keyof ResponseTypesByStatus],
        paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
      >({
        endpoint: API_ENDPOINT,
        method: API_METHOD,
        data: { email: logInWithEmailContext.state.email.value },
      });

      setLoading(false);

      console.log(data);
      console.log(response);

      if (response.status === 200) {
        setSent(true);
      }
    }
  }

  return (
    <Modal
      onExit={() =>
        logInWithEmailContext.dispatch({
          type: 'SET_ACTIVE',
          payload: false,
        })
      }
      show={logInWithEmailContext.state.isActive}
    >
      <div id="login-with-email">
        <div className="w-full">
          {!sent ? (
            <form onSubmit={handleSubmit}>
              <h2 className="text-center">Send Email</h2>
              <p className="text-center">
                Enter the email address of an existing account, and we'll send
                you a secure login link.
              </p>

              <div>
                <label htmlFor="email">Email</label>
                <h4>
                  <InputText
                    state={logInWithEmailContext.state.email}
                    setState={(state: InputState) => {
                      logInWithEmailContext.dispatch({
                        type: 'SET_EMAIL',
                        payload: state,
                      });
                    }}
                    id="email"
                    minLength={
                      openapi_schema.components.schemas.UserCreate.properties
                        .email.minLength
                    }
                    maxLength={
                      openapi_schema.components.schemas.UserCreate.properties
                        .email.maxLength
                    }
                    type="email"
                    isValid={isEmailValid}
                  />
                </h4>
              </div>
              <button
                className={`button-primary ${
                  !logInWithEmailContext.state.valid && 'button-invalid'
                }`}
                type="submit"
                disabled={!logInWithEmailContext.state.valid}
              >
                <div className="flex flex-row justify-center items-center p-1">
                  <h6 className="mb-0 leading-none">
                    {loading ? (
                      <span className="loader-secondary"></span>
                    ) : (
                      'Send Email'
                    )}
                  </h6>
                </div>
              </button>
            </form>
          ) : (
            <>
              <p>Check your inbox</p>
              <button
                className="button-primary"
                onClick={() => {
                  logInWithEmailContext.dispatch({
                    type: 'SET_ACTIVE',
                    payload: false,
                  });
                }}
              >
                Okay!
              </button>
            </>
          )}
        </div>
      </div>
    </Modal>
  );
}

export { LogInWithEmail };
