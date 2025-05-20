import React, { useEffect, useState, useContext } from 'react';
import { ValidatedInputString } from '../Form/ValidatedInputString';
import { ValidatedInputState, defaultValidatedInputState } from '../../types';
import openapi_schema from '../../../../openapi_schema.json';
import { AuthContext } from '../../contexts/Auth';
import { components } from '../../openapi_schema';
import { ToastContext } from '../../contexts/Toast';
import { patchMe } from '../../services/apiServices';
import { Button1 } from '../Utils/Button';
import { isPasswordValid } from '../../services/isPasswordValid';

export function UpdatePassword() {
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

  useEffect(() => {
    if (password.status !== 'valid') {
      setConfirmPassword((prev) => ({
        ...prev,
        status: 'invalid',
        message: 'Password is invalid',
      }));
    } else if (password.value !== confirmPassword.value) {
      setConfirmPassword((prev) => ({
        ...prev,
        status: 'invalid',
        message: 'Passwords do not match',
      }));
    } else {
      setConfirmPassword((prev) => ({
        ...prev,
        status: 'valid',
      }));
    }
  }, [confirmPassword.value, password]);

  async function handleUpdatePassword(e: React.FormEvent) {
    e.preventDefault();
    if (valid && authContext.state.user !== null) {
      let toastId = toastContext.makePending({
        message: 'Updating password...',
      });

      const response = await patchMe.call({
        authContext,
        data: {
          password: password.value,
        },
      });

      if (response.status === 200) {
        const apiData = response.data as (typeof patchMe.responses)['200'];
        setPassword({ ...defaultValidatedInputState<string>('') });
        setConfirmPassword({ ...defaultValidatedInputState<string>('') });
        toastContext.update(toastId, {
          message: 'Updated password',
          type: 'success',
        });
        authContext.setState({
          ...authContext.state,
          user: apiData,
        });
      } else {
        toastContext.update(toastId, {
          message: 'Error updating password',
          type: 'error',
        });
      }
    }
  }

  return (
    <form onSubmit={handleUpdatePassword} className="flex flex-col space-y-2">
      <div>
        <label htmlFor="password">Password</label>
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
          isValid={isPasswordValid}
          checkValidity={true}
          showStatus={password.value !== '' || confirmPassword.value !== ''}
        />
      </div>
      <div>
        <label htmlFor="confirmPassword">Confirm Password</label>
        <ValidatedInputString
          state={confirmPassword}
          setState={setConfirmPassword}
          id="confirmPassword"
          type="password"
          checkValidity={true}
          showStatus={password.value !== '' || confirmPassword.value !== ''}
        />
      </div>
      <Button1 type="submit" disabled={!valid}>
        Update Password
      </Button1>
    </form>
  );
}
