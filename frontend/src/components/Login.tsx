import React, { useState, useContext } from 'react';
import { LoginContext } from '../contexts/Login';
import { Modal } from './Modal';

function Login() {
  let context = useContext(LoginContext);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  function handleLogin(e: React.FormEvent) {
    e.preventDefault();
  }

  if (!context.state) {
    return null;
  } else {
    return (
      // if user presses escape key, close the modal

      <Modal close={context.toggle}>
        <div className="flex justify-center items-center">
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
              <button onClick={context.toggle}>Cancel</button>
              <button>Login</button>
            </form>
          </div>
        </div>
      </Modal>
    );
  }
}

//   );

export { Login };

// const clientId =
//   '1855778612-f8jc05eb675d4226q50kqea1vp354ra0.apps.googleusercontent.com';

// const handleLoginSuccess = async (response: any) => {
//   console.log('Success:', response);
//   const { credential } = response;

//   try {
//     const res = await fetch(
//       'https://your-backend-server.com/api/auth/google',
//       {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({ credential }),
//       }
//     );

//     if (res.ok) {
//       const data = await res.json();
//       console.log('Backend response:', data);
//       // Handle successful authentication (e.g., store tokens, redirect user)
//     } else {
//       console.error('Backend error:', res.statusText);
//     }
//   } catch (error) {
//     console.error('Network error:', error);
//   }
// };

// return (
//   <GoogleOAuthProvider clientId={clientId}>
//     <h1>Google OAuth in React</h1>
//     <GoogleLogin
//       onSuccess={(response: any) => {
//         console.log('Success:', response);
//       }}
//       onError={() => {
//         console.log('Error');
//       }}
//     />
//   </GoogleOAuthProvider>
// );
