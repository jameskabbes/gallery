import React, { useEffect, useState, useContext } from 'react';
import { InputText } from '../Form/InputText';
import { InputState, defaultInputState } from '../../types';
import openapi_schema from '../../../../openapi_schema.json';
import { AuthContext } from '../../contexts/Auth';
import { patchUserFunc } from './patchUserFunc';
import { components } from '../../openapi_schema';
import { ToastContext } from '../../contexts/Toast';

interface Props {
  userId: components['schemas']['UserPublic']['id'];
}

function UpdatePassword({ userId }: Props) {
  const [password, setPassword] = useState<InputState>({
    ...defaultInputState,
  });
  const [confirmPassword, setConfirmPassword] = useState<InputState>({
    ...defaultInputState,
  });
  const [valid, setValid] = useState<boolean>(false);
  const authContext = useContext(AuthContext);
  const toastContext = useContext(ToastContext);

  useEffect(() => {
    setValid(password.status === 'valid' && confirmPassword.status === 'valid');
  }, [password.status, confirmPassword.status]);

  async function handleUpdatePassword(e: React.FormEvent) {
    e.preventDefault();
    if (valid && authContext.state.user !== null) {
      let { data, response } = await patchUserFunc(
        userId,
        {
          password: password.value,
        },
        authContext,
        toastContext
      );

      if (response.status === 200) {
        setPassword({ ...defaultInputState });
        setConfirmPassword({ ...defaultInputState });
      }
    }
  }

  return (
    <form onSubmit={handleUpdatePassword} className="flex flex-col space-y-2">
      <InputText
        state={password}
        setState={setPassword}
        id="password"
        minLength={
          openapi_schema.components.schemas.UserUpdate.properties.password
            .anyOf[0].minLength
        }
        maxLength={
          openapi_schema.components.schemas.UserUpdate.properties.password
            .anyOf[0].maxLength
        }
        type="password"
        placeholder="New password"
      />
      <InputText
        state={confirmPassword}
        setState={setConfirmPassword}
        id="confirmPassword"
        minLength={
          openapi_schema.components.schemas.UserUpdate.properties.password
            .anyOf[0].minLength
        }
        maxLength={
          openapi_schema.components.schemas.UserUpdate.properties.password
            .anyOf[0].maxLength
        }
        type="password"
        placeholder="Confirm new password"
        isValid={(confirmPassword: InputState['value']) => {
          if (password.status !== 'valid') {
            return { valid: false, message: 'Password is invalid' };
          } else if (password.value !== confirmPassword) {
            return { valid: false, message: 'Passwords do not match' };
          } else {
            return { valid: true };
          }
        }}
      />
      <button
        className={`button-primary ${!valid && 'button-invalid'}`}
        type="submit"
        disabled={!valid}
      >
        <p className="flex flex-row justify-center items-center">
          Update Password
        </p>
      </button>
    </form>
  );
}

export { UpdatePassword };
