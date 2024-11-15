import React, { useContext } from 'react';
import { paths, operations, components } from '../../openapi_schema';
import { AuthContextType, ToastContextType } from '../../types';

import { UpdateUsername } from '../User/UpdateUsername';
import { UpdatePassword } from '../User/UpdatePassword';
import { UpdateUser } from '../User/UpdateUser';
import { Button1 } from '../Utils/Button';
import { SetDeleteAccountModal } from '../Profile/DeleteAccount';
import { GlobalModalsContext } from '../../contexts/GlobalModals';

interface Props {
  authContext: AuthContextType;
  toastContext: ToastContextType;
}

function Profile({ authContext, toastContext }: Props) {
  const globalModalsContext = useContext(GlobalModalsContext);

  return (
    <div>
      <h2 className="mb-4">Profile</h2>
      {/* <UpdateUser user={authContext.state.user} />
      <UpdateUsername user={authContext.state.user} />
      <UpdatePassword /> */}
      <Button1 onClick={() => SetDeleteAccountModal({ globalModalsContext })}>
        Delete Account
      </Button1>
    </div>
  );
}

export { Profile };
