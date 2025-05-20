import { useGoogleLogin } from '@react-oauth/google';
import { postLogInGoogle } from '../../services/apiServices';
import { useContext } from 'react';
import { ToastContext } from '../../contexts/Toast';
import { AuthContext } from '../../contexts/Auth';
import { AuthModalsContext } from '../../contexts/AuthModals';

export function useLogInWithGoogle() {
  const toastContext = useContext(ToastContext);
  const authContext = useContext(AuthContext);
  const authModalsContext = useContext(AuthModalsContext);

  return useGoogleLogin({
    onSuccess: async (res) => {
      const toastId = toastContext.makePending({
        message: 'Logging in with Google...',
      });

      const { data, status } = await postLogInGoogle.call({
        authContext,
        data: {
          access_token: res.access_token,
        },
      });

      if (status == 200) {
        toastContext.update(toastId, {
          message: 'Logged in with Google',
          type: 'success',
        });
        const apiData = data as (typeof postLogInGoogle.responses)['200'];
        authModalsContext.activate(null);
      } else {
        toastContext.update(toastId, {
          message: 'Could not log in with Google',
          type: 'error',
        });
      }
    },
  });
}
