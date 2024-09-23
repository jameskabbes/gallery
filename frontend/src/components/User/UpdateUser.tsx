import React, { useEffect, useState, useContext } from 'react';
import { InputText, ValidityCheckReturn } from '../Form/InputText';
import { InputState, defaultInputState } from '../../types';
import { paths, operations, components } from '../../openapi_schema';
import openapi_schema from '../../../../openapi_schema.json';
import { AuthContext } from '../../contexts/Auth';
import { ToastContext } from '../../contexts/Toast';
import { patchUserFunc } from './patchUserFunc';
import { isEmailAvailable } from './isEmailAvailable';
import { isEmailValid } from './isEmailValid';

interface Props {
  user: components['schemas']['UserPrivate'];
}

function UpdateUser({ user }: Props) {
  const [startingEmail, setStartingEmail] = useState<string>(user.email);
  const [email, setEmail] = useState<InputState>({
    ...defaultInputState,
    value: user.email,
  });
  const [valid, setValid] = useState<boolean>(false);
  const [modified, setModified] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const authContext = useContext(AuthContext);
  const toastContext = useContext(ToastContext);

  useEffect(() => {
    setValid(email.status === 'valid' && modified);
  }, [email.status, modified]);

  useEffect(() => {
    setModified(email.value !== startingEmail);
  }, [email.value, loading]);

  function reset() {
    setEmail({ ...defaultInputState, value: startingEmail });
  }

  async function handleUpdateUser(e: React.FormEvent) {
    e.preventDefault();
    if (valid && authContext.state.user !== null) {
      setLoading(true);
      const { data, response } = await patchUserFunc(
        user.id,
        {
          email: email.value,
        },
        authContext,
        toastContext
      );
      setLoading(false);
      if (response.status === 200) {
        setStartingEmail(email.value);
      }
    }
  }

  async function isEmailAvailableConditional(
    email: components['schemas']['UserUpdate']['email']
  ) {
    if (email === user.email) {
      return true;
    } else {
      return await isEmailAvailable(email);
    }
  }

  function isEmailValidConditional(
    email: components['schemas']['UserUpdate']['email']
  ): ValidityCheckReturn {
    if (email === user.email) {
      return { valid: true };
    } else {
      return isEmailValid(email);
    }
  }

  return (
    <form onSubmit={handleUpdateUser} className="flex flex-col space-y-2">
      <div className="grid grid-cols-[auto,1fr] gap-x-2 gap-y-1">
        <label htmlFor="email">
          <p>Email</p>
        </label>
        <InputText
          state={email}
          setState={setEmail}
          id="email"
          type="email"
          minLength={
            openapi_schema.components.schemas.UserUpdate.properties.email
              .anyOf[0].minLength
          }
          maxLength={
            openapi_schema.components.schemas.UserUpdate.properties.email
              .anyOf[0].maxLength
          }
          checkAvailability={true}
          isAvailable={isEmailAvailableConditional}
          isValid={isEmailValidConditional}
        />
      </div>
      <div className="flex flex-row space-x-2">
        <button
          className={`button-secondary ${!modified && 'button-invalid'} flex-1`}
          type="button"
          onClick={reset}
          disabled={!modified}
        >
          <p>Cancel</p>
        </button>
        <button
          className={`button-primary ${!valid && 'button-invalid'} flex-1`}
          type="submit"
          disabled={!valid}
        >
          <p className="flex flex-row justify-center items-center">
            {loading ? (
              <span className="loader-secondary"></span>
            ) : (
              'Update User'
            )}
          </p>
        </button>
      </div>
    </form>
  );
}

export { UpdateUser };
