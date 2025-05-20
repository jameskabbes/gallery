import { postLogOut } from '../../services/apiServices';
import { AuthContextType, ToastContextType } from '../../types';

export async function logOut(
  authContext: AuthContextType,
  toastContext: ToastContextType
) {
  let toastId = toastContext.makePending({
    message: 'Logging out...',
  });
  const response = await postLogOut.call({
    authContext,
  });
  if (response.status === 200) {
    authContext.logOut(toastId);
  } else {
    toastContext.update(toastId, {
      message: 'Error logging out',
      type: 'error',
    });
  }
}
