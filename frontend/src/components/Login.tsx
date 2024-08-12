import React, { useState, useContext, useEffect } from 'react';
import { ModalsContext } from '../contexts/Modals';
import { callApiBase, callBackendApi } from '../utils/Api';
import validator from 'validator';

import { CheckOrX } from './Form/CheckOrX';

import { toast } from 'react-toastify';
import { toastTemplate } from './Toast';

import { Modal } from './Modal';

type Modes = 'login' | 'register';

function Login() {
  const [mode, setMode] = useState<Modes>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [validEmail, setValidEmail] = useState(false);
  const [validPassword, setValidPassword] = useState(false);
  const [valid, setValid] = useState(false);
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

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    modalsContext.dispatch({ type: 'POP' });

    // Simple validation
    if (valid) {
      let toastId = toast.loading('Logging in');

      const { data, response } = await callBackendApi({
        endpoint: '/token/',
        method: 'POST',
        data: {
          username: email,
          password: password,
        },
      });

      console.log(response);
      console.log('Form submitted:', { email, password });
      modalsContext.dispatch({ type: 'POP' });

      toast.update(toastId, {
        ...toastTemplate,
        render: `Logged in`,
        type: 'success',
      });
    } else {
      console.log('Invalid form submission');
    }
  }

  return (
    <Modal>
      <div key="login">
        {/* modes */}
        <form onSubmit={handleLogin} className="flex flex-col space-y-2">
          <div className="slider-container my-2">
            <input
              type="radio"
              id="signIn"
              name="mode"
              value="login"
              checked={mode === 'login'}
              onChange={() => setMode('login')}
            />
            <label htmlFor="signIn">Sign In</label>

            <input
              type="radio"
              id="register"
              name="mode"
              value="register"
              checked={mode === 'register'}
              onChange={() => setMode('register')}
            />
            <label htmlFor="register">Register</label>
          </div>
          <div className="text-input flex flex-row items-center">
            <input
              className="bg-color-lighter focus:outline-none"
              type="email"
              id="email"
              value={email}
              placeholder="email"
              onChange={(e) => setEmail(e.target.value)}
              required
            />

            <span>
              <CheckOrX value={validEmail} />
            </span>
          </div>
          <div className="text-input flex flex-row items-center focus:border-4">
            <input
              className="bg-color-lighter focus:outline-none"
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="password"
              required
            />
            <span>
              <CheckOrX value={validPassword} />
            </span>
          </div>
          <input
            className={`focus:outline-none ${
              valid ? 'button-primary' : 'button-secondary'
            }`}
            type="submit"
            value={
              mode === 'login'
                ? 'Sign In'
                : mode === 'register'
                ? 'Register'
                : 'Sign In'
            }
          />
        </form>
      </div>
    </Modal>
  );
}

export { Login };
