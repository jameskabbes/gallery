import React from 'react';
import { useGoogleLogin } from '@react-oauth/google';

function useLogInWithGoogle() {
  const googleLogin = useGoogleLogin({
    onSuccess: (response) => {
      console.log(response);
    },
  });

  function logInWithGoogle() {
    googleLogin();
  }

  return { logInWithGoogle };
}

export { useLogInWithGoogle };
