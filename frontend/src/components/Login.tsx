import React, { useState, useContext, useEffect } from 'react';
import { ModalsContext } from '../contexts/Modals';
import { callApiBase, callBackendApi } from '../utils/Api';
import validator from 'validator';
import { paths, operations, components } from '../openapi_schema';
import { ExtractResponseTypes } from '../types';
import { CheckOrX } from './Form/CheckOrX';

import { toast } from 'react-toastify';
import { toastTemplate } from './Toast';

import { Modal } from './Modal';
import { GoogleLogin } from '@react-oauth/google';

const API_PATH = '/token/';
const API_METHOD = 'post';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_PATH][typeof API_METHOD]['responses']
>;

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [validEmail, setValidEmail] = useState(false);
  const [validPassword, setValidPassword] = useState(false);
  const [valid, setValid] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [showError, setShowError] = useState(false);
  const modalsContext = useContext(ModalsContext);

  useEffect(() => {
    setValidEmail(validator.isEmail(email));
  }, [email]);
  useEffect(() => {
    setValidPassword(password.length > 0);
  }, [password]);
  useEffect(() => {
    setValid(validEmail && validPassword);
  }, [validEmail, validPassword]);

  async function sleep(ms: number) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();

    // Simple validation
    if (valid) {
      setLoading(true);
      setShowError(false);

      await sleep(2000);

      const { data, response } = await callBackendApi<
        components['schemas']['Token'],
        components['schemas']['LoginRequest']
      >({
        endpoint: API_PATH,
        method: API_METHOD,
        data: {
          email: email,
          password: password,
        },
      });
      setLoading(false);

      if (response.status === 200) {
        const responseData = data as ResponseTypesByStatus['200'];

        // set the jwt token in local storage
        localStorage.setItem('token', responseData.access_token);

        modalsContext.dispatch({ type: 'POP' });
      } else if (response.status === 401) {
        setErrorMessage('Invalid username or password.');
        setShowError(true);
        setTimeout(() => {
          setShowError(false);
        }, 5000); // Hide error message after 5 seconds
      }
    }
  }

  return (
    <Modal>
      <div id="login">
        {/* modes */}
        <form onSubmit={handleLogin} className="flex flex-col space-y-2">
          <h4 className="text-center">Login</h4>
          <div className="flex flex-row h-10 items-center justify-center">
            {loading ? (
              <h2 className="loader"></h2>
            ) : showError ? (
              <div className="error-message">
                <p>{errorMessage}</p>
              </div>
            ) : null}
          </div>
          <div className="text-input flex flex-row items-center space-x-2">
            <input
              className="bg-inherit focus:outline-none"
              type="email"
              id="email"
              value={email}
              placeholder="email"
              onChange={(e) => setEmail(e.target.value)}
              required
              formNoValidate
            />

            <span>
              <CheckOrX value={validEmail} />
            </span>
          </div>
          <div className="text-input flex flex-row items-center space-x-2">
            <input
              className="bg-inherit focus:outline-none"
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="password"
              required
              formNoValidate
            />
            <span>
              <CheckOrX value={validPassword} />
            </span>
          </div>

          <button
            className={`${valid ? 'button-valid' : 'button-invalid'}`}
            type="submit"
          >
            <p className="flex flex-row justify-center items-center">Login</p>
          </button>
        </form>
        {/* <GoogleLogin onSuccess={() => {}}></GoogleLogin> */}
      </div>
    </Modal>
  );
}

export { Login };
