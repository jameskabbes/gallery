import React, { useContext, useEffect, useState } from 'react';
import {
  CallApiProps,
  ValidatedInputState,
  ToastContext as ToastContextType,
  ExtractResponseTypes,
  AuthContext as AuthContextType,
  defaultValidatedInputState,
  GlobalModalsContext as GlobalModalsContextType,
} from '../../types';
import { useApiCall } from '../../utils/Api';
import { paths, operations, components } from '../../openapi_schema';
import {
  deleteAPIKey,
  ResponseTypesByStatus as DeleteAPIKeyResponseTypes,
} from '../../services/api/deleteAPIKey';

import {
  postAPIKey,
  ResponseTypesByStatus as PostAPIKeyResponseTypes,
} from '../../services/api/postAPIKey';

import { postAPIKeyScope } from '../../services/api/postAPIKeyScope';
import { deleteAPIKeyScope } from '../../services/api/deleteAPIKeyScope';

import { GlobalModalsContext } from '../../contexts/GlobalModals';
import { useConfirmationModal } from '../../utils/useConfirmationModal';

import { CiClock2 } from 'react-icons/ci';
import { IoHourglassOutline } from 'react-icons/io5';
import { IoChevronForwardOutline } from 'react-icons/io5';
import { IoChevronDownOutline } from 'react-icons/io5';
import { ValidatedInputString } from '../Form/ValidatedInputString';

import openapi_schema from '../../../../openapi_schema.json';
import { ValidatedInputDatetimeLocal } from '../Form/ValidatedInputDatetimeLocal';
import { Button1, Button2, ButtonSubmit } from '../Utils/Button';
import { Card1, CardButton } from '../Utils/Card';
import { Toggle1 } from '../Utils/Toggle';

const API_ENDPOINT = '/settings/api-keys/page/';
const API_METHOD = 'get';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

type TAPIKeys = ResponseTypesByStatus['200']['api_keys'];
type TSetAPIKeys = React.Dispatch<React.SetStateAction<TAPIKeys>>;
type TScopes = ResponseTypesByStatus['200']['scopes'];
type TAPIKeyScopes = ResponseTypesByStatus['200']['api_key_scopes'];
type TSetAPIKeyScopes = React.Dispatch<React.SetStateAction<TAPIKeyScopes>>;

const loadingAPIKeyName = 'loading...';

async function handleAddAPIKeyScope(
  scope: components['schemas']['Scope'],
  apiKey: components['schemas']['APIKey'],
  setAPIKeyScopes: TSetAPIKeyScopes,
  toastContext: ToastContextType,
  authContext: AuthContextType
) {
  let toastId = toastContext.makePending({
    message: `Adding ${scope.name} to ${apiKey.name}`,
  });

  const { data, response } = await postAPIKeyScope(
    authContext,
    apiKey.id,
    scope.id
  );
  if (response.status === 204) {
    toastContext.update(toastId, {
      message: `Added ${scope.name} to ${apiKey.name}`,
      type: 'success',
    });
    setAPIKeyScopes((prev) => ({
      ...prev,
      [apiKey.id]: [...prev[apiKey.id], scope.id],
    }));
  } else {
    toastContext.update(toastId, {
      message: `Error adding ${scope.name} to ${apiKey.name}`,
      type: 'error',
    });
  }
}

async function handleDeleteAPIKeyScope(
  scope: components['schemas']['Scope'],
  apiKey: components['schemas']['APIKey'],
  setAPIKeyScopes: TSetAPIKeyScopes,
  toastContext: ToastContextType,
  authContext: AuthContextType
) {
  let toastId = toastContext.makePending({
    message: `Removing ${scope.name} from ${apiKey.name}`,
  });

  const { data, response } = await deleteAPIKeyScope(
    authContext,
    apiKey.id,
    scope.id
  );

  if (response.status === 204) {
    toastContext.update(toastId, {
      message: `Removed ${scope.name} from ${apiKey.name}`,
      type: 'success',
    });
    setAPIKeyScopes((prev) => ({
      ...prev,
      [apiKey.id]: prev[apiKey.id].filter((id) => id !== scope.id),
    }));
  } else {
    toastContext.update(toastId, {
      message: `Error removing ${scope.name} from ${apiKey.name}`,
      type: 'error',
    });
  }
}

interface APIKeyScopeRowProps {
  scope: components['schemas']['Scope'];
  apiKey: components['schemas']['APIKey'];
  apiKeyScopes: TAPIKeyScopes;
  setAPIKeyScopes: TSetAPIKeyScopes;
  toastContext: ToastContextType;
  authContext: AuthContextType;
}

function APIKeyScopeRow({
  scope,
  apiKey,
  apiKeyScopes,
  setAPIKeyScopes,
  toastContext,
  authContext,
}: APIKeyScopeRowProps) {
  const [loading, setLoading] = useState<boolean>(false);
  const [toggle, setToggle] = useState<boolean>(
    apiKeyScopes[apiKey.id].includes(scope.id)
  );

  async function handleToggle() {
    setLoading(true);
    let toggleSnapshot = toggle;
    setToggle((prev) => !prev);

    if (toggleSnapshot) {
      // was on, now turning off
      await handleDeleteAPIKeyScope(
        scope,
        apiKey,
        setAPIKeyScopes,
        toastContext,
        authContext
      );
    } else {
      // was off, now turning on
      await handleAddAPIKeyScope(
        scope,
        apiKey,
        setAPIKeyScopes,
        toastContext,
        authContext
      );
    }
    setLoading(false);
  }

  return (
    <div
      className="flex flex-row items-center space-x-1"
      key={`${apiKey.id}-${scope.id}`}
    >
      <Toggle1
        onClick={(e) => {
          e.stopPropagation();
          handleToggle();
        }}
        state={toggle}
        disabled={loading}
      />

      <p>{scope.name}</p>
    </div>
  );
}

interface APIKeyRowProps {
  apiKeyId: components['schemas']['APIKey']['id'];
  apiKeys: TAPIKeys;
  setAPIKeys: TSetAPIKeys;
  scopes: TScopes;
  apiKeyScopes: TAPIKeyScopes;
  setAPIKeyScopes: TSetAPIKeyScopes;
  toastContext: ToastContextType;
  authContext: AuthContextType;
  checkConfirmation: ReturnType<
    typeof useConfirmationModal
  >['checkConfirmation'];
}

function APIKeyRow({
  apiKeyId,
  apiKeys,
  setAPIKeys,
  scopes,
  apiKeyScopes,
  setAPIKeyScopes,
  toastContext,
  authContext,
  checkConfirmation,
}: APIKeyRowProps) {
  const [isEditing, setIsEditing] = useState(false);

  async function handleDeleteAPIKey(apiKeyId: string) {
    let toastId = toastContext.makePending({
      message: `Deleting API Key ${apiKeys[apiKeyId].name}`,
    });

    const apiKeyToDelete = apiKeys[apiKeyId];
    const newAPIKeys = { ...apiKeys };
    delete newAPIKeys[apiKeyId];
    setAPIKeys(newAPIKeys);

    const apiKeyScopesToDelete = apiKeyScopes[apiKeyId];
    const newAPIKeyScopes = { ...apiKeyScopes };
    delete newAPIKeyScopes[apiKeyId];
    setAPIKeyScopes(newAPIKeyScopes);

    const { data, response } = await deleteAPIKey(authContext, apiKeyId);

    if (response.status === 204) {
      const apiData = data as DeleteAPIKeyResponseTypes['204'];
      toastContext.update(toastId, {
        message: `Deleted API Key ${apiKeyToDelete.name}`,
        type: 'success',
      });
    } else {
      toastContext.update(toastId, {
        message: `Error deleting API Key ${apiKeyToDelete.name}`,
        type: 'error',
      });
      setAPIKeys({ ...apiKeys, [apiKeyId]: apiKeyToDelete });
      setAPIKeyScopes({ ...apiKeyScopes, [apiKeyId]: apiKeyScopesToDelete });
    }
  }

  return (
    <CardButton
      onClick={() =>
        setIsEditing((prev) => {
          if (apiKeys[apiKeyId].name !== loadingAPIKeyName) {
            return !prev;
          }
        })
      }
      className="flex flex-col"
    >
      <div className="flex flex-row w-full items-center space-x-2">
        <span>
          {isEditing ? <IoChevronDownOutline /> : <IoChevronForwardOutline />}
        </span>
        <div className="flex flex-col flex-1">
          <h3 className="mb-4 ml-4 text-left">{apiKeys[apiKeyId].name}</h3>
          <div className="flex flex-row items-center space-x-2">
            <p>
              <CiClock2 />
            </p>
            <p>
              Issued:{' '}
              {new Date(apiKeys[apiKeyId].issued).toLocaleString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: 'numeric',
                minute: 'numeric',
              })}
            </p>
          </div>
          <div className="flex flex-row items-center space-x-2">
            <p>
              <IoHourglassOutline />
            </p>
            <p>
              Expires:{' '}
              {new Date(apiKeys[apiKeyId].expiry).toLocaleString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: 'numeric',
                minute: 'numeric',
              })}
            </p>
          </div>
        </div>
        <Button2
          onClick={(e) => {
            e.stopPropagation();
            checkConfirmation(
              {
                title: 'Delete API Key?',
                confirmText: 'Delete',
                message: `Are you sure you want to delete the API Key ${apiKeys[apiKeyId].name}?`,
                onConfirm: () => {
                  handleDeleteAPIKey(apiKeyId);
                },
                onCancel: () => {},
              },
              {
                key: 'delete-api-key',
              }
            );
          }}
        >
          <span className="text-error-500">Delete</span>
        </Button2>
      </div>
      {isEditing && (
        <div className="flex flex-col">
          {/* map through all scopes */}
          {Object.keys(scopes).map((scopeId) => (
            <APIKeyScopeRow
              key={scopeId}
              scope={scopes[scopeId]}
              apiKey={apiKeys[apiKeyId]}
              apiKeyScopes={apiKeyScopes}
              setAPIKeyScopes={setAPIKeyScopes}
              toastContext={toastContext}
              authContext={authContext}
            />
          ))}
        </div>
      )}
    </CardButton>
  );
}

interface AddAPIKeyProps {
  authContext: AuthContextType;
  toastContext: ToastContextType;
  globalModalsContext: GlobalModalsContextType;
  setAPIKeys: TSetAPIKeys;
  setAPIKeyScopes: TSetAPIKeyScopes;
}

function AddAPIKey({
  authContext,
  toastContext,
  globalModalsContext,
  setAPIKeys,
  setAPIKeyScopes,
}: AddAPIKeyProps) {
  const [name, setName] = useState<ValidatedInputState<string>>({
    ...defaultValidatedInputState<string>(''),
  });
  const [expiry, setExpiry] = useState<ValidatedInputState<Date>>({
    ...defaultValidatedInputState<Date>(
      new Date(new Date().setMonth(new Date().getMonth() + 1))
    ),
  });

  const [valid, setValid] = useState(false);

  useEffect(() => {
    setValid(name.status === 'valid' && expiry.status === 'valid');
  }, [name.status, expiry.status]);

  async function addAPIKey(event: React.FormEvent) {
    event.preventDefault();
    globalModalsContext.setModal(null);

    let toastId = toastContext.makePending({
      message: 'Creating API Key...',
    });

    // make a random 16 character string
    const tempId = Math.random().toString();

    const tempAPIKey: PostAPIKeyResponseTypes['200'] = {
      id: tempId,
      user_id: authContext.state.user.id,
      issued: new Date().toISOString(),
      name: loadingAPIKeyName,
      expiry: new Date(expiry['value']).toISOString(),
    };

    setAPIKeys((prevAPIKeys) => ({
      ...prevAPIKeys,
      [tempId]: tempAPIKey,
    }));
    setAPIKeyScopes((prev) => ({ ...prev, [tempId]: [] }));

    // wait 10 seconds
    await new Promise((resolve) => setTimeout(resolve, 10000));

    const { data, response } = await postAPIKey(authContext, {
      expiry: new Date(expiry['value']).toISOString(),
      name: name['value'],
    });

    if (response.status === 200) {
      const apiData = data as PostAPIKeyResponseTypes['200'];
      toastContext.update(toastId, {
        message: `Created API Key ${apiData.name}`,
        type: 'success',
      });

      setAPIKeys((prevAPIKeys) => {
        const newAPIKeys = { ...prevAPIKeys };
        delete newAPIKeys[tempId];
        newAPIKeys[apiData.id] = apiData;
        return newAPIKeys;
      });
      setAPIKeyScopes((prev) => {
        const newAPIKeyScopes = { ...prev };
        delete newAPIKeyScopes[tempId];
        newAPIKeyScopes[apiData.id] = [];
        return newAPIKeyScopes;
      });
    } else {
      toastContext.update(toastId, {
        message: 'Error creating API Key',
        type: 'error',
      });

      setAPIKeys((prevAPIKeys) => {
        const newAPIKeys = { ...prevAPIKeys };
        delete newAPIKeys[tempId];
        return newAPIKeys;
      });
      setAPIKeyScopes((prev) => {
        const newAPIKeyScopes = { ...prev };
        delete newAPIKeyScopes[tempId];
        return newAPIKeyScopes;
      });
    }
  }

  return (
    <div id="add-api-key">
      <form onSubmit={addAPIKey} className="flex flex-col space-y-4">
        <header>Add API Key</header>
        <fieldset className="flex flex-col space-y-4">
          <section>
            <label htmlFor="api-key-name">Name</label>
            <ValidatedInputString
              state={name}
              setState={setName}
              id="api-key-name"
              type="text"
              minLength={
                openapi_schema.components.schemas.APIKeyCreate.properties.name
                  .minLength
              }
              maxLength={
                openapi_schema.components.schemas.APIKeyCreate.properties.name
                  .maxLength
              }
              required={true}
              checkValidity={true}
              showStatus={true}
            />
          </section>
          <section>
            <label htmlFor="api-key-expiry">Expiry</label>
            <ValidatedInputDatetimeLocal
              state={expiry}
              setState={setExpiry}
              id="api-key-expiry"
              required={true}
              showStatus={true}
            />
          </section>
        </fieldset>
        <ButtonSubmit disabled={!valid}>Add API Key</ButtonSubmit>
      </form>
    </div>
  );
}

interface APIKeysProps {
  authContext: AuthContextType;
  toastContext: ToastContextType;
}

function APIKeys({ authContext, toastContext }: APIKeysProps): JSX.Element {
  const globalModalsContext = useContext(GlobalModalsContext);
  const { checkConfirmation } = useConfirmationModal();

  const [apiKeys, setAPIKeys] = useState<
    ResponseTypesByStatus['200']['api_keys']
  >({});
  const [scopes, setScopes] = useState<ResponseTypesByStatus['200']['scopes']>(
    {}
  );
  const [apiKeyScopes, setAPIKeyScopes] = useState<
    ResponseTypesByStatus['200']['api_key_scopes']
  >({});

  const {
    data: apiData,
    loading,
    response,
  } = useApiCall<ResponseTypesByStatus[keyof ResponseTypesByStatus]>({
    endpoint: API_ENDPOINT,
    method: API_METHOD,
  });

  useEffect(() => {
    if (apiData && response.status === 200) {
      const data = apiData as ResponseTypesByStatus['200'];
      setAPIKeys(data.api_keys);
      setScopes(data.scopes);
      setAPIKeyScopes(data.api_key_scopes);
    }
  }, [apiData, response]);

  return (
    <>
      {authContext.state.user === null ? (
        <>
          <h2>API Keys</h2>
          <p>Login to view your API keys.</p>
        </>
      ) : (
        <>
          <div className="flex flex-row justify-between mb-4">
            <h2>API Keys</h2>
            <Button1
              onClick={() => {
                globalModalsContext.setModal({
                  component: (
                    <AddAPIKey
                      authContext={authContext}
                      toastContext={toastContext}
                      globalModalsContext={globalModalsContext}
                      setAPIKeys={setAPIKeys}
                      setAPIKeyScopes={setAPIKeyScopes}
                    />
                  ),
                  key: 'modal-make-api-key',
                });
              }}
            >
              Add API Key
            </Button1>
          </div>
          <div className="flex flex-col space-y-4">
            {Object.keys(apiKeys).map((apiKeyId) => (
              <APIKeyRow
                key={apiKeyId}
                apiKeyId={apiKeyId}
                apiKeys={apiKeys}
                setAPIKeys={setAPIKeys}
                scopes={scopes}
                apiKeyScopes={apiKeyScopes}
                setAPIKeyScopes={setAPIKeyScopes}
                toastContext={toastContext}
                authContext={authContext}
                checkConfirmation={checkConfirmation}
              />
            ))}
          </div>
        </>
      )}
    </>
  );
}

export { APIKeys };
