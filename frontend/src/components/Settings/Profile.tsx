import React from 'react';
import { paths, operations, components } from '../../openapi_schema';
import { AuthContextType, ToastContextType } from '../../types';

import { UpdateUsername } from '../User/UpdateUsername';
import { UpdatePassword } from '../User/UpdatePassword';
import { UpdateUser } from '../User/UpdateUser';

interface Props {
  authContext: AuthContextType;
  toastContext: ToastContextType;
}

function Profile({ authContext, toastContext }: Props) {
  return (
    <div>
      <h2 className="mb-4">Profile</h2>
      {/* <UpdateUser user={authContext.state.user} />
      <UpdateUsername user={authContext.state.user} />
      <UpdatePassword /> */}
    </div>
  );
}

export { Profile };
