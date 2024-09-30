import React from 'react';
import { paths, operations, components } from '../../openapi_schema';
import {
  CallApiProps,
  ToastContext,
  ExtractResponseTypes,
  AuthContext,
} from '../../types';

interface Props {
  authContext: AuthContext;
  toastContext: ToastContext;
}

function Profile({ authContext, toastContext }: Props) {
  return (
    <div>
      <h1>Profile</h1>
    </div>
  );
}

export { Profile };
