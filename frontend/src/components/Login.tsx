import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';

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
