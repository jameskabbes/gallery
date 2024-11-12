import React, { useEffect, useState, useContext } from 'react';
import { ValidatedInputString } from '../Form/ValidatedInputString';
import { ValidatedInputState, defaultValidatedInputState } from '../../types';
import openapi_schema from '../../../../openapi_schema.json';
import { AuthContext } from '../../contexts/Auth';
import { components } from '../../openapi_schema';
import { ToastContext } from '../../contexts/Toast';
import {
  patchUserFunc,
  PatchUserResponses,
} from '../../services/api/patchUserFunc';

function UpdatePassword() {
  const [password, setPassword] = useState<ValidatedInputState<string>>({
    ...defaultValidatedInputState<string>(''),
  });
  const [confirmPassword, setConfirmPassword] = useState<
    ValidatedInputState<string>
  >({
    ...defaultValidatedInputState<string>(''),
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
      let toastId = toastContext.makePending({
        message: 'Updating password...',
      });

      const { data, status } = await patchUserFunc(authContext, {
        password: password.value,
      });

      if (status === 200) {
        const apiData = data as PatchUserResponses['200'];
        setPassword({ ...defaultInputState });
        setConfirmPassword({ ...defaultInputState });
        toastContext.update(toastId, {
          message: 'Updated user',
          type: 'success',
        });
        authContext.setState({
          ...authContext.state,
          user: apiData,
        });
      } else {
        let message = 'Error updating password';
        if (status === 404 || status === 409) {
          const apiData = data as PatchUserResponses['404' | '409'];
          message = apiData.detail;
        }
        toastContext.update(toastId, {
          message: message,
          type: 'error',
        });
      }
    }
  }

  return (
    <form onSubmit={handleUpdatePassword} className="flex flex-col space-y-2">
      <ValidatedInputString
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
      <ValidatedInputString
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
