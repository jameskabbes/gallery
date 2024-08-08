import React, { useState, useContext, useEffect } from 'react';
import { ModalsContext } from '../contexts/Modals';
import { IoClose } from 'react-icons/io5';
import { callApiBase, callBackendApi } from '../utils/Api';

import { toast } from 'react-toastify';
import { toastTemplate } from './Toast';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [valid, setValid] = useState(false);

  useEffect(() => {
    setValid(email.length > 0 && password.length > 0);
  }, [email, password]);

  let modalsContext = useContext(ModalsContext);

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
    <div className="card" key="login">
      <p className="flex flex-row justify-end">
        <IoClose
          onClick={() => modalsContext.dispatch({ type: 'POP' })}
          className="cursor-pointer"
        />
      </p>

      <h3 className="text-center">Sign In</h3>

      <form onSubmit={handleLogin} className="flex flex-col space-y-2">
        <input
          className="flex flex-row"
          type="email"
          id="email"
          value={email}
          placeholder="email"
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          className="flex flex-row"
          type="password"
          id="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="password"
          required
        />
        <input
          className={
            `flex flex-row w-full` +
            (valid ? ' button-primary' : 'button-secondary')
          }
          type="submit"
          value="Sign In"
        />
      </form>
    </div>
  );
}

export { Login };
