import React, { useContext, useEffect, useState } from 'react';
import {
  CallApiProps,
  InputState,
  InputStateAny,
  ToastContext,
  ExtractResponseTypes,
  AuthContext,
  defaultInputState,
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

import { GlobalModalsContext } from '../../contexts/GlobalModals';
import { useConfirmationModal } from '../../utils/useConfirmationModal';

import { CiClock2 } from 'react-icons/ci';
import { IoHourglassOutline } from 'react-icons/io5';
import { IoChevronForwardOutline } from 'react-icons/io5';
import { IoChevronDownOutline } from 'react-icons/io5';
import { Input } from '../Form/Input';
import { InputText } from '../Form/InputText';
import { isDatetimeValid } from '../../services/isDatetimeValid';

import openapi_schema from '../../../../openapi_schema.json';
import { InputDatetimeLocal } from '../Form/InputDatetimeLocal';

const API_ENDPOINT = '/api-keys/';
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

  const [apiKeys, setAPIKeys] = useState<{
    [key: string]: ResponseTypesByStatus['200'][number];
  }>({});

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
      const apiKeysObject = (apiData as ResponseTypesByStatus['200']).reduce(
        (acc, apiKey) => {
          acc[apiKey.id] = apiKey;
          return acc;
        },
        {} as { [key: string]: ResponseTypesByStatus['200'][number] }
      );
      setAPIKeys(apiKeysObject);
    }
  }, [apiData, response]);

  function AddAPIKey() {
    const [name, setName] = useState<InputState<string>>({
      ...defaultInputState<string>(''),
    });
    const [expiry, setExpiry] = useState<InputStateAny<Date>>({
      ...defaultInputState<Date>(
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
      const tempID = Array.from(
        { length: 16 },
        () => Math.random().toString(36)[2]
      ).join('');

      const tempAPIKey: PostAPIKeyResponseTypes['200'] = {
        id: tempID,
        user_id: authContext.state.user.id,
        issued: new Date().toISOString(),
        name: loadingAPIKeyName,
        expiry: new Date(expiry['value']).toISOString(),
      };

      setAPIKeys((prevAPIKeys) => ({
        ...prevAPIKeys,
        [tempID]: tempAPIKey,
      }));

      // wait for two seoncd
      await new Promise((resolve) => setTimeout(resolve, 2000));

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
          delete newAPIKeys[tempID];
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
          delete newAPIKeys[tempID];
          return newAPIKeys;
        });
      }
    }

    return (
      <div id="add-api-key">
        <form onSubmit={addAPIKey} className="flex flex-col space-y-2">
          <span className="title">Add API Key</span>
          <div>
            <label htmlFor="api-key-name">Name</label>
            <InputText
              state={name}
              setState={(state: InputState<string>) => {
                setName(state);
              }}
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
            />
          </div>
          <div>
            <label htmlFor="api-key-expiry">Expiry</label>
            <InputDatetimeLocal
              state={expiry}
              setState={setExpiry}
              id="api-key-expiry"
              required={true}
            />
          </div>

          <button type="submit" disabled={!valid}>
            <span className="leading-none mb-0">Add API Key</span>
          </button>
        </form>
      </div>
    );
  }

  function APIKeyRow({ apiKey }: { apiKey: components['schemas']['APIKey'] }) {
    const [isEditing, setIsEditing] = useState(false);

    return (
      <div key={apiKey.id} className="button-tertiary">
        <div className="flex flex-row items-center space-x-2">
          <div className="flex flex-col">
            <button onClick={() => setIsEditing((prev) => !prev)}>
              {isEditing ? (
                <IoChevronDownOutline />
              ) : (
                <IoChevronForwardOutline />
              )}
            </button>
          </div>
          <div className="flex flex-col flex-1">
            <h4>{apiKey.name}</h4>
            <p className="flex flex-row items-center space-x-2">
              <CiClock2 />
              <span>
                Issued:{' '}
                {new Date(apiKey.issued).toLocaleString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                  hour: 'numeric',
                  minute: 'numeric',
                })}
              </span>
            </p>
            <p className="flex flex-row items-center space-x-2">
              <IoHourglassOutline />
              <span>
                Expires:{' '}
                {new Date(apiKey.expiry).toLocaleString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                  hour: 'numeric',
                  minute: 'numeric',
                })}
              </span>
            </p>
          </div>
          <div className="flex flex-col">
            <button
              onClick={() => {
                checkConfirmation({
                  title: 'Delete API Key?',
                  confirmText: 'Delete',
                  message: `Are you sure you want to delete the API Key ${apiKey.name}?`,
                  onConfirm: () => {
                    handleDeleteAPIKey(apiKey.id);
                    globalModalsContext.setModal(null);
                  },
                  onCancel: () => {
                    globalModalsContext.setModal(null);
                  },
                });
              }}
              className="button-tertiary"
            >
              <span className="text-error-500">Delete</span>
            </button>
          </div>
        </div>
        {isEditing && (
          <div className="flex flex-col">
            <p>Editing...</p>
          </div>
        )}
      </div>
    );
  }

  async function handleDeleteAPIKey(apiKeyId: string) {
    let toastId = toastContext.makePending({
      message: `Deleting API Key ${apiKeys[apiKeyId].name}...`,
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
    <>
      {authContext.state.user === null ? (
        <p>Login to view your API keys.</p>
      ) : (
        <>
          <div className="flex flex-row justify-between p-1">
            <h2>API Keys</h2>
            <button
              className="button-primary"
              onClick={() => {
                globalModalsContext.setModal({
                  component: <AddAPIKey />,
                  key: 'modal-make-api-key',
                });
              }}
            >
              Add Key
            </button>
          </div>
          <div className="p-2">
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
