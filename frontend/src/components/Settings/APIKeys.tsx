import React, { useContext, useEffect, useState } from 'react';
import {
  CallApiProps,
  ValidatedInputState,
  ToastContext,
  ExtractResponseTypes,
  AuthContext,
  defaultValidatedInputState,
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
import { Card1 } from '../Utils/Card';
import { ValidatedInputToggle } from '../Form/ValidatedInputToggle';
import { Toggle1 } from '../Utils/Toggle';

const API_ENDPOINT = '/settings/api-keys/page/';
const API_METHOD = 'get';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

interface Props {
  authContext: AuthContext;
  toastContext: ToastContext;
}

function APIKeys({ authContext, toastContext }: Props): JSX.Element {
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

  const loadingAPIKeyName = 'loading...';

  const {
    data: apiData,
    loading,
    response,
  } = useApiCall<ResponseTypesByStatus[keyof ResponseTypesByStatus]>(
    {
      endpoint: API_ENDPOINT,
      method: API_METHOD,
    },
    true
  );

  useEffect(() => {
    if (apiData && response.status === 200) {
      const data = apiData as ResponseTypesByStatus['200'];
      setAPIKeys(data.api_keys);
      setScopes(data.scopes);
      setAPIKeyScopes(data.api_key_scopes);
    }
  }, [apiData, response]);

  function AddAPIKey() {
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

      const { data, response } = await postAPIKey({
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

  async function handleAddAPIKeyScope(
    apiKeyId: components['schemas']['APIKey']['id'],
    scopeId: components['schemas']['Scope']['id']
  ) {
    // let toastId = toastContext.makePending({
    //   message: `Adding ${scopes[scopeId].name} to ${apiKeys[apiKeyId].name}`,
    // });
    const { data, response } = await postAPIKeyScope(apiKeyId, scopeId);
    if (response.status === 204) {
      // toastContext.update(toastId, {
      //   message: `Added ${scopes[scopeId].name} to ${apiKeys[apiKeyId].name}`,
      //   type: 'success',
      // });
      // setAPIKeyScopes((prev) => ({
      //   ...prev,
      //   [apiKeyId]: [...prev[apiKeyId], scopeId],
      // }));
    } else {
      // toastContext.update(toastId, {
      //   message: `Error adding ${scopes[scopeId].name} to ${apiKeys[apiKeyId].name}`,
      //   type: 'error',
      // });
    }
  }
  async function handleDeleteAPIKeyScope(
    apiKeyId: components['schemas']['APIKey']['id'],
    scopeId: components['schemas']['Scope']['id']
  ) {
    // let toastId = toastContext.makePending({
    //   message: `Removing ${scopes[scopeId].name} from ${apiKeys[apiKeyId].name}`,
    // });

    const { data, response } = await deleteAPIKeyScope(apiKeyId, scopeId);

    if (response.status === 204) {
      // toastContext.update(toastId, {
      //   message: `Removed ${scopes[scopeId].name} from ${apiKeys[apiKeyId].name}`,
      //   type: 'success',
      // });
      setAPIKeyScopes((prev) => ({
        ...prev,
        [apiKeyId]: prev[apiKeyId].filter((id) => id !== scopeId),
      }));
    } else {
      // toastContext.update(toastId, {
      //   message: `Error removing ${scopes[scopeId].name} from ${apiKeys[apiKeyId].name}`,
      //   type: 'error',
      // });
    }
  }

  function APIKeyScopeRow({
    apiKeyId,
    scopeId,
  }: {
    apiKeyId: components['schemas']['APIKey']['id'];
    scopeId: components['schemas']['Scope']['id'];
  }) {
    const [loading, setLoading] = useState<boolean>(false);
    const [toggle, setToggle] = useState<boolean>(
      apiKeyScopes[apiKeyId].includes(scopeId)
    );

    async function handleToggle() {
      setLoading(true);
      let toggleSnapshot = toggle;
      setToggle((prev) => !prev);

      if (toggleSnapshot) {
        // was on, now turning off
        handleDeleteAPIKeyScope(apiKeyId, scopeId);
      } else {
        // was off, now turning on
        handleAddAPIKeyScope(apiKeyId, scopeId);
      }

      setLoading(false);
    }

    return (
      <div
        className="flex flex-row items-center space-x-1"
        key={`${apiKeyId}-${scopeId}`}
      >
        <Toggle1 state={toggle} onClick={handleToggle} disabled={loading} />
        <p>{scopes[scopeId].name}</p>
      </div>
    );
  }

  function APIKeyRow({ apiKey }: { apiKey: components['schemas']['APIKey'] }) {
    const [isEditing, setIsEditing] = useState(false);

    async function handleDeleteAPIKey(apiKeyId: string) {
      let toastId = toastContext.makePending({
        message: `Deleting API Key ${apiKeys[apiKeyId].name}`,
      });

      const apiKeyToDelete = apiKeys[apiKeyId];
      const newAPIKeys = { ...apiKeys };
      delete newAPIKeys[apiKeyId];
      setAPIKeys(newAPIKeys);

      const { data, response } = await deleteAPIKey(apiKeyId);

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
      }
    }

    return (
      <Card1 key={apiKey.id} onClick={() => setIsEditing((prev) => !prev)}>
        <div className="flex flex-row items-center space-x-2">
          <div className="flex flex-col">
            <span>
              {isEditing ? (
                <IoChevronDownOutline />
              ) : (
                <IoChevronForwardOutline />
              )}
            </span>
          </div>
          <div className="flex flex-col flex-1">
            <h3 className="mb-4">{apiKey.name}</h3>
            <div className="flex flex-row items-center space-x-2">
              <p>
                <CiClock2 />
              </p>
              <p>
                Issued:{' '}
                {new Date(apiKey.issued).toLocaleString('en-US', {
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
                {new Date(apiKey.expiry).toLocaleString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                  hour: 'numeric',
                  minute: 'numeric',
                })}
              </p>
            </div>
          </div>
          <div className="flex flex-col">
            <Button2
              onClick={() => {
                checkConfirmation(
                  {
                    title: 'Delete API Key?',
                    confirmText: 'Delete',
                    message: `Are you sure you want to delete the API Key ${apiKey.name}?`,
                    onConfirm: () => {
                      handleDeleteAPIKey(apiKey.id);
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
        </div>
        {isEditing && (
          <div className="flex flex-col">
            {/* map through all scopes */}
            {Object.keys(scopes).map((scopeId) => (
              <APIKeyScopeRow
                key={scopeId}
                apiKeyId={apiKey.id}
                scopeId={scopeId}
              />
            ))}
          </div>
        )}
      </Card1>
    );
  }

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
                  component: <AddAPIKey />,
                  key: 'modal-make-api-key',
                });
              }}
            >
              Add API Key
            </Button1>
          </div>
          <div className="flex flex-col space-y-4">
            {Object.keys(apiKeys).map((key) => (
              <div key={apiKeys[key].id}>
                <APIKeyRow apiKey={apiKeys[key]} />
              </div>
            ))}
          </div>
        </>
      )}
    </>
  );
}

export { APIKeys };
