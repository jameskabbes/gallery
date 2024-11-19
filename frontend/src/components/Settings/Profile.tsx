import React, { useContext } from 'react';
import { paths, operations, components } from '../../openapi_schema';
import { AuthContextType, ToastContextType } from '../../types';

import { UpdateUsername } from '../User/UpdateUsername';
import { UpdatePassword } from '../User/UpdatePassword';
import { Button1 } from '../Utils/Button';
import { setDeleteAccountModal } from '../User/DeleteAccount';
import { GlobalModalsContext } from '../../contexts/GlobalModals';
import { useConfirmationModal } from '../../utils/useConfirmationModal';
import { UpdateEmail } from '../User/UpdateEmail';

interface Props {
  authContext: AuthContextType;
  toastContext: ToastContextType;
}

function Profile({ authContext, toastContext }: Props) {
  const globalModalsContext = useContext(GlobalModalsContext);
  const { checkTextConfirmation } = useConfirmationModal();

  if (authContext.state.user !== null) {
    return (
      <div>
        <h2 className="mb-4">Profile</h2>
        <div className="flex flex-col max-w-sm space-y-6">
          <UpdateEmail user={authContext.state.user} />
          <UpdateUsername user={authContext.state.user} />
          <UpdatePassword />
        </div>
        <Button1
          onClick={() =>
            setDeleteAccountModal({
              checkTextConfirmation,
              authContext,
              toastContext,
              globalModalsContext,
            })
          }
        >
          Delete Account
        </Button1>
      </div>
    );
  }
}

export { Profile };
