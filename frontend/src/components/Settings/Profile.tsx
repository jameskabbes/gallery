import React, { useContext } from 'react';
import { paths, operations, components } from '../../openapi_schema';
import { AuthContextType, ToastContextType } from '../../types';

import { UpdateUsername } from '../User/UpdateUsername';
import { UpdatePassword } from '../User/UpdatePassword';
import { Button1 } from '../Utils/Button';
import { setDeleteAccountModal } from '../User/DeleteAccount';
import { ModalsContext } from '../../contexts/Modals';
import { useConfirmationModal } from '../../utils/useConfirmationModal';
import { UpdateEmail } from '../User/UpdateEmail';
import { Surface } from '../Utils/Surface';

interface Props {
  authContext: AuthContextType;
  toastContext: ToastContextType;
}

export function Profile({ authContext, toastContext }: Props) {
  const modalsContext = useContext(ModalsContext);
  const { activateTextConfirmation } = useConfirmationModal();

  if (authContext.state.user !== null) {
    return (
      <div>
        <h2 className="mb-4">Profile</h2>
        <div className="flex flex-col max-w-md space-y-6">
          <div className="flex flex-col space-y-2">
            <Surface>
              <hr />
            </Surface>
            <UpdateEmail user={authContext.state.user} />
          </div>
          <div className="flex flex-col space-y-2">
            <Surface>
              <hr />
            </Surface>
            <UpdateUsername user={authContext.state.user} />
          </div>
          <div className="flex flex-col space-y-2">
            <Surface>
              <hr />
            </Surface>
            <UpdatePassword />
          </div>
          <div className="flex flex-col space-y-2">
            <Surface>
              <hr />
            </Surface>
            <h4>Delete Account</h4>
            <p>
              Delete your entire account. All galleries, images, videos, api
              keys, etc. will be deleted.{' '}
              <strong>This cannot be undone.</strong>
            </p>
            <Button1
              onClick={() =>
                setDeleteAccountModal({
                  activateTextConfirmation,
                  authContext,
                  toastContext,
                  modalsContext,
                })
              }
            >
              Delete Account
            </Button1>
          </div>
        </div>
      </div>
    );
  }
}
