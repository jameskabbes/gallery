import React, { useContext, useState } from 'react';
import { deleteUser, DeleteUserResponses } from '../../services/api/deleteUser';
import {
  AuthContextType,
  ModalsContextType,
  ToastContextType,
} from '../../types';
import { useConfirmationModal } from '../../utils/useConfirmationModal';

interface Props {
  checkTextConfirmation: ReturnType<
    typeof useConfirmationModal
  >['checkTextConfirmation'];
  authContext: AuthContextType;
  toastContext: ToastContextType;
  modalsContext: ModalsContextType;
}

function setDeleteAccountModal({
  checkTextConfirmation,
  authContext,
  toastContext,
  modalsContext,
}: Props) {
  async function handleDeleteUser() {
    modalsContext.deleteModal('delete-account');
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

  checkTextConfirmation(
    {
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
    {
      modalKey: 'delete-account',
    }
  );
}

export { setDeleteAccountModal };
