import React, { useEffect, useState, useContext } from 'react';
import { InputText } from '../Form/InputText';
import { InputState, defaultInputState } from '../../types';
import openapi_schema from '../../../../openapi_schema.json';
import { AuthContext } from '../../contexts/Auth';
import { patchUserFunc } from './patchUserFunc';
import { components } from '../../openapi_schema';

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

  useEffect(() => {
    setValid(
      password.status === 'valid' &&
        confirmPassword.status === 'valid' &&
        authContext.state.isActive
    );
  }, [password.status, confirmPassword.status, authContext.state.isActive]);

  async function handleUpdatePassword(e: React.FormEvent) {
    e.preventDefault();
    if (valid && authContext.state.isActive) {
      let resp = await patchUserFunc(
        userId,
        {
          password: password.value,
        },
        authContext.dispatch
      );
      console.log(resp);
      setPassword({ ...defaultInputState });
      setConfirmPassword({ ...defaultInputState });
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
        className={`${valid ? 'button-valid' : 'button-invalid'}`}
        type="submit"
        disabled={!valid}
      >
        <p className="flex flex-row justify-center items-center">
          Change Password
        </p>
      </button>
    </form>
  );
}

export { UpdatePassword };
