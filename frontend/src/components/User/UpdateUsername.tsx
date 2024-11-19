import React, { useEffect, useState, useContext } from 'react';
import openapi_schema from '../../../../openapi_schema.json';
import { AuthContext } from '../../contexts/Auth';
import { ToastContext } from '../../contexts/Toast';
import { components } from '../../openapi_schema';
import {
  getIsUsernameAvailable,
  isUsernameAvailable,
} from '../../services/api/getIsUsernameAvailable';
import { patchUser, PatchUserResponses } from '../../services/api/patchUser';
import { defaultValidatedInputState, ValidatedInputState } from '../../types';
import { ValidatedInputString } from '../Form/ValidatedInputString';
import { Button1, Button2 } from '../Utils/Button';
import { ValidatedInputToggle } from '../Form/ValidatedInputToggle';
import { Toggle1 } from '../Utils/Toggle';

interface Props {
  user: components['schemas']['UserPrivate'];
}

function UpdateUsername({ user }: Props) {
  const [startingUsername, setStartingUsername] = useState<
    Props['user']['username']
  >(user.username === null ? '' : user.username);

  const [isPublic, setIsPublic] = useState<boolean>(false);

  const [username, setUsername] = useState<ValidatedInputState<string>>({
    ...defaultValidatedInputState<string>(startingUsername),
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
      setLoading(true);
      let toastId = toastContext.makePending({
        message: 'Updating username...',
      });

      const response = await patchUser(authContext, {
        username: username.value,
      });

      setLoading(false);

      if (response.status === 200) {
        const apiData = response.data as PatchUserResponses['200'];
        setStartingUsername(username.value);
        toastContext.update(toastId, {
          message: 'Updated username',
          type: 'success',
        });
        authContext.setState({
          ...authContext.state,
          user: apiData,
        });
      } else {
        toastContext.update(toastId, {
          message: 'Error updating username',
          type: 'error',
        });
      }
    }
  }

  return (
    <form onSubmit={handleUpdateUsername} className="flex flex-col space-y-2">
      <div>
        <label htmlFor="username">Username</label>
        <ValidatedInputString
          state={username}
          setState={setUsername}
          id="username"
          type="text"
          minLength={
            openapi_schema.components.schemas.UserUpdate.properties.username
              .anyOf[0].minLength
          }
          maxLength={
            openapi_schema.components.schemas.UserUpdate.properties.username
              .anyOf[0].maxLength
          }
          checkValidity={true}
          checkAvailability={true}
          isAvailable={isUsernameAvailable}
          showStatus={true}
        />
      </div>
      <div className="flex flex-row space-x-2">
        <Button2
          className="flex-1"
          onClick={(e) => {
            setUsername({
              ...defaultValidatedInputState<string>(startingUsername),
            });
          }}
          disabled={!modified}
        >
          Cancel
        </Button2>
        <Button1 type="submit" className="flex-1" disabled={!valid}>
          Update Username
        </Button1>
      </div>
    </form>
  );
}

export { UpdateUsername };
