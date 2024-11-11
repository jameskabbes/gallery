import React, { Component } from 'react';
import { paths, operations, components } from '../../openapi_schema';
import { callApi } from '../../utils/api';
import { useConfirmationModal } from '../../utils/useConfirmationModal';
import { PostLogOutResponses, postLogOut } from '../../services/api/postLogOut';
import { ApiResponse, AuthContextType, ToastContextType } from '../../types';

async function logOut(
  authContext: AuthContextType,
  toastContext: ToastContextType
) {
  let toastId = toastContext.makePending({
    message: 'Logging out...',
  });
  const response = await postLogOut(authContext);
  if (response.status === 200) {
    authContext.logOut(toastId);
  } else {
    toastContext.update(toastId, {
      message: 'Error logging out',
      type: 'error',
    });
  }
}

export { logOut };
