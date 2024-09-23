import React, { useEffect, useState, useContext } from 'react';
import { InputText } from '../Form/InputText';
import { InputState, defaultInputState } from '../../types';
import openapi_schema from '../../../../openapi_schema.json';
import { AuthContext } from '../../contexts/Auth';
import { ToastContext } from '../../contexts/Toast';
import { patchUserFunc } from './patchUserFunc';
import { components } from '../../openapi_schema';
import { isUsernameAvailable } from './isUsernameAvailable';

interface Props {
  user: components['schemas']['UserPrivate'];
}

function UpdateUsername({ user }: Props) {
  const [startingUsername, setStartingUsername] = useState<
    Props['user']['username']
  >(user.username === null ? '' : user.username);
  const [username, setUsername] = useState<InputState>({
    ...defaultInputState,
  });
  const [valid, setValid] = useState<boolean>(false);
  const [modified, setModified] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const authContext = useContext(AuthContext);
  const toastContext = useContext(ToastContext);

  useEffect(() => {
    setValid(username.status === 'valid' && modified);
  }, [username.status, modified]);

  useEffect(() => {
    setModified(username.value !== startingUsername);
  }, [username.value, loading]);

  async function handleUpdateUsername(e: React.FormEvent) {
    e.preventDefault();
    if (valid && authContext.state.user !== null) {
      let { data, response } = await patchUserFunc(
        user.id,
        {
          username: username.value,
        },
        authContext,
        toastContext
      );

      if (response.status === 200) {
        setUsername({ ...defaultInputState });
      }
    }
  }

  return (
    <form onSubmit={handleUpdateUsername} className="flex flex-col space-y-2">
      <div>
        <label htmlFor="username">
          <p>Username</p>
        </label>
        <InputText
          state={username}
          setState={setUsername}
          id="username"
          minLength={
            openapi_schema.components.schemas.UserPublic.properties.username
              .anyOf[0].minLength
          }
          maxLength={
            openapi_schema.components.schemas.UserPublic.properties.username
              .anyOf[0].maxLength
          }
          type="text"
          isAvailable={isUsernameAvailable}
        />
      </div>
      <div className="flex flex-row space-x-2">
        <button
          className={`button-secondary ${!modified && 'button-invalid'} flex-1`}
          type="button"
          onClick={() => {
            setUsername({ ...defaultInputState, value: startingUsername });
          }}
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
              'Change Username'
            )}
          </p>
        </button>
      </div>
    </form>
  );
}

export { UpdateUsername };
