import React from 'react';
import { paths, operations, components } from '../../openapi_schema';
import {
  CallApiProps,
  ToastContext,
  ExtractResponseTypes,
  AuthContext,
} from '../../types';

import { UpdateUsername } from '../User/UpdateUsername';
import { UpdatePassword } from '../User/UpdatePassword';
import { UpdateUser } from '../User/UpdateUser';

interface Props {
  authContext: AuthContext;
  toastContext: ToastContext;
}

function Profile({ authContext, toastContext }: Props) {
  return (
    <div>
      {/* <UpdateUser user={authContext.state.user} />
      <UpdateUsername user={authContext.state.user} />
      <UpdatePassword /> */}
    </div>
  );
}

export { Profile };
