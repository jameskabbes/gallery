import React, { useState, useContext, useEffect } from 'react';
import { ModalsContext } from '../contexts/Modals';
import { callApiBase, callBackendApi } from '../utils/Api';
import validator from 'validator';

import { CheckOrX } from './Form/CheckOrX';

import { toast } from 'react-toastify';
import { toastTemplate } from './Toast';

import { Modal } from './Modal';

function Login() {
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
          <h4 className="text-center">Login</h4>
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
            Login
          </button>
        </form>
      </div>
    </Modal>
  );
}

export { Login };
