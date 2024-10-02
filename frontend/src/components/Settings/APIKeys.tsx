import React, { useEffect, useState } from 'react';
import { CallApiProps, ToastContext } from '../../types';
import { useApiCall } from '../../utils/Api';
import { paths, operations, components } from '../../openapi_schema';
import { ExtractResponseTypes, AuthContext } from '../../types';
import { deleteAPIKey } from '../../services/api/deleteAPIKey';
import { postAPIKey } from '../../services/api/postAPIKey';

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
    console.log(apiKeys);

    const apiKeyToDelete = apiKeys[apiKeyId];

    const newAPIKeys = { ...apiKeys };
    delete newAPIKeys[apiKeyId];
    setAPIKeys(newAPIKeys);

    const { data, response } = await deleteAPIKey(apiKeyId, toastContext);

    console.log(data);
    console.log(response);

    if (response.status !== 204) {
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
              postAPIKey(
                {
                  user_id: authContext.state.user.id,
                  expiry: new Date().toISOString(),
                  name: Array.from(
                    { length: 16 },
                    () => Math.random().toString(36)[2]
                  ).join(''),
                },
                toastContext
              );
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
                      handleDeleteAPIKey(key);
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
