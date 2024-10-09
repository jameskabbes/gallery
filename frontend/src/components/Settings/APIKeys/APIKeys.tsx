import React, { useContext, useEffect, useState } from 'react';
import { CallApiProps, ToastContext } from '../../../types';
import { useApiCall } from '../../../utils/Api';
import { paths, operations, components } from '../../../openapi_schema';
import { ExtractResponseTypes, AuthContext } from '../../../types';
import {
  deleteAPIKey,
  ResponseTypesByStatus as DeleteAPIKeyResponseTypes,
} from '../../../services/api/deleteAPIKey';

import { GlobalModalsContext } from '../../../contexts/GlobalModals';
import { useConfirmationModal } from '../../../utils/useConfirmationModal';

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
      <h2>API Keys</h2>
      {authContext.state.user === null ? (
        <p>Login to view your API keys.</p>
      ) : (
        <>
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
          <div>
            {Object.keys(apiKeys).map((key) => {
              const apiKey = apiKeys[key];
              return (
                <div key={key} className="flex flex-row">
                  <p>
                    Issued:{' '}
                    {new Date(apiKey.issued).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                    })}
                  </p>
                  <p>{apiKey.name}</p>
                  <button
                    onClick={() => {
                      checkConfirmation({
                        title: 'Delete API Key?',
                        confirmText: 'Delete',
                        message: `Are you sure you want to delete the API Key ${apiKey.name}?`,
                        onConfirm: () => {
                          handleDeleteAPIKey(key);
                          globalModalsContext.setModal(null);
                        },
                        onCancel: () => {
                          globalModalsContext.setModal(null);
                        },
                      });
                    }}
                    className="button-primary"
                  >
                    Delete
                  </button>
                </div>
              );
            })}
          </div>
        </>
      )}
    </>
  );
}

export { APIKeys };
