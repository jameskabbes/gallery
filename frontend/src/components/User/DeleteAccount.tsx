import React, { useContext, useState } from 'react';
import { deleteUser, DeleteUserResponses } from '../../services/api/deleteUser';
import {
  AuthContextType,
  ModalsContextType,
  ToastContextType,
} from '../../types';
import { useConfirmationModal } from '../../utils/useConfirmationModal';

interface Props {
  activateTextConfirmation: ReturnType<
    typeof useConfirmationModal
  >['activateTextConfirmation'];
  authContext: AuthContextType;
  toastContext: ToastContextType;
  modalsContext: ModalsContextType;
}

const modalKey = 'modal-confirmation-delete-account';

function setDeleteAccountModal({
  activateTextConfirmation,
  authContext,
  toastContext,
  modalsContext,
}: Props) {
  async function handleDeleteUser() {
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
      authContext.logOut();
    } else {
      toastContext.update(toastId, {
        message: 'Error deleting account',
        type: 'error',
      });
    }
  }

  activateTextConfirmation({
    key: modalKey,
    componentProps: {
      title: 'Delete Account?',
      message: (
        <p>
          This operation will delete your account and all your data.{' '}
          <strong>This cannot be undone. </strong>
        </p>
      ),
      target: 'delete',
      onConfirm: () => handleDeleteUser(),
    },
  });
}

export { setDeleteAccountModal };
