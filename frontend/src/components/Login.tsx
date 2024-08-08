import React, { useState, useContext } from 'react';
import { Modal } from './Modal';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  function handleLogin(e: React.FormEvent) {
    e.preventDefault();
  }

  return (
    <Modal onCancel={() => {}}>
      <div className="card">
        <form onSubmit={handleLogin}>
          <div className="form-group">
            <label htmlFor="email">Email:</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">Password:</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button onClick={() => console.log('cancel')}>Cancel</button>
          <button>Login</button>
        </form>
      </div>
    </Modal>
  );
}

export { Login };
