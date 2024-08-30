import React, { useEffect, useState, useContext } from 'react';
import { InputText } from '../Form/InputText';
import { InputState, defaultInputState } from '../../types';
import { paths, operations, components } from '../../openapi_schema';
import openapi_schema from '../../../../openapi_schema.json';
import { AuthContext } from '../../contexts/Auth';
import { patchUserFunc } from './patchUserFunc';
import { isUsernameAvailable } from './isUsernameAvailable';
import { isUsernameValid } from './isUsernameValid';
import { isEmailAvailable } from './isEmailAvailable';
import { isEmailValid } from './isEmailValid';

interface Props {
  user: components['schemas']['UserPrivate'];
}

function UpdateUser({ user }: Props) {
  const [startingUsername, setStartingUsername] = useState<string>(
    user.username
  );
  const [startingEmail, setStartingEmail] = useState<string>(user.email);

  const [username, setUsername] = useState<InputState>({
    ...defaultInputState,
    value: user.username,
  });
  const [email, setEmail] = useState<InputState>({
    ...defaultInputState,
    value: user.email,
  });
  const [valid, setValid] = useState<boolean>(false);
  const [modified, setModified] = useState<boolean>(false);
  const authContext = useContext(AuthContext);

  useEffect(() => {
    setValid(
      email.status === 'valid' &&
        username.status === 'valid' &&
        modified &&
        authContext.state.isActive
    );
  }, [email.status, username.status, modified, authContext.state.isActive]);

  useEffect(() => {
    setModified(
      email.value !== startingEmail || username.value !== startingUsername
    );
  }, [email.value, username.value]);

  function reset() {
    setUsername({ ...defaultInputState, value: startingUsername });
    setEmail({ ...defaultInputState, value: startingEmail });
  }

  async function handleUpdateUser(e: React.FormEvent) {
    e.preventDefault();
    if (valid && authContext.state.isActive) {
      const { data, response } = await patchUserFunc(
        user.id,
        {
          username: username.value,
          email: email.value,
        },
        authContext.dispatch
      );
      if (response.status === 200) {
        setStartingUsername(username.value);
        setStartingEmail(email.value);
      }
    }
  }

  async function isUsernameAvailableConditional(
    username: components['schemas']['UserUpdate']['username']
  ) {
    if (username === user.username) {
      return true;
    } else {
      return await isUsernameAvailable(username);
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

  return (
    <form onSubmit={handleUpdateUser} className="flex flex-col space-y-2">
      <div className="grid grid-cols-[auto,1fr] gap-x-2 gap-y-1">
        <label htmlFor="username">username</label>
        <InputText
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
          checkAvailability={true}
          isAvailable={isUsernameAvailableConditional}
          isValid={isUsernameValid}
        />
        <label htmlFor="email">email</label>
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
          isValid={isEmailValid}
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
            Update User
          </p>
        </button>
      </div>
    </form>
  );
}

export { UpdateUser };
