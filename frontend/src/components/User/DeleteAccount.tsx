import React, { useContext, useState } from 'react';
import {
  defaultValidatedInputState,
  GlobalModalsContextType,
  ValidatedInputState,
} from '../../types';
import { ButtonSubmit } from '../Utils/Button';
import { ValidatedInputString } from '../Form/ValidatedInputString';
import { deleteUser, DeleteUserResponses } from '../../services/api/deleteUser';
import { AuthContext } from '../../contexts/Auth';
import { ToastContext } from '../../contexts/Toast';
import { toast } from 'react-toastify';

interface DeleteAccountProps {
  globalModalsContext: GlobalModalsContextType;
}

function DeleteAccount({ globalModalsContext }: DeleteAccountProps) {
  const authContext = useContext(AuthContext);
  const toastContext = useContext(ToastContext);
  const [confirm, setConfirm] = useState<ValidatedInputState<string>>({
    ...defaultValidatedInputState<string>(''),
  });

  async function handleDeleteUser(e: React.FormEvent) {
    e.preventDefault();
    globalModalsContext.clearModal();

    const toastId = toastContext.makePending({
      message: 'Deleting account...',
    });

    const response = await deleteUser(authContext);

    if (response.status === 204) {
      const data = response.data as DeleteUserResponses['204'];
      toastContext.update(toastId, {
        message: 'Account deleted',
        type: 'success',
      });
      console.log('Account deleted');
      authContext.logOut();
    } else {
      toastContext.update(toastId, {
        message: 'Error deleting account',
        type: 'error',
      });
    }
  }

  return (
    <form onSubmit={handleDeleteUser} className="flex flex-col space-y-8">
      <header>Delete Account?</header>

      <p>
        This operation will delete your account and all your data.{' '}
        <strong>This cannot be undone. </strong>
      </p>
      <p className="text-center">
        To proceed, type{' '}
        <code>
          <strong>delete</strong>
        </code>{' '}
        in the field below.
      </p>

      <ValidatedInputString
        state={confirm}
        setState={setConfirm}
        checkValidity={true}
        isValid={(value) =>
          value === 'delete'
            ? { valid: true }
            : { valid: false, message: 'Invalid entry' }
        }
        showStatus={true}
      />

      <ButtonSubmit disabled={confirm.status !== 'valid'}>
        Delete Account
      </ButtonSubmit>
    </form>
  );
}

interface SetDeleteAccountModalProps extends DeleteAccountProps {}

function SetDeleteAccountModal({
  globalModalsContext,
  ...rest
}: SetDeleteAccountModalProps) {
  globalModalsContext.setModal({
    component: (
      <DeleteAccount globalModalsContext={globalModalsContext} {...rest} />
    ),
    key: 'delete-account',
    className: 'max-w-[400px] w-full',
  });
}

export { DeleteAccount, SetDeleteAccountModal };
