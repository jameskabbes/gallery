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
  deleteApiKey,
  ResponseTypesByStatus as DeleteApiKeyResponseTypes,
} from '../../services/api/deleteApiKey';

import {
  postApiKey,
  ResponseTypesByStatus as PostApiKeyResponseTypes,
} from '../../services/api/postApiKey';

import { postApiKeyScope } from '../../services/api/postApiKeyScope';
import { deleteApiKeyScope } from '../../services/api/deleteApiKeyScope';

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
import {
  getApiKeyJWT,
  ResponseTypesByStatus as GetApiKeyJWTResponseTypes,
} from '../../services/api/getApiKeyJwt';
import { toast } from 'react-toastify';
import { Surface } from '../Utils/Surface';
import config from '../../../../config.json';
import {
  scopeIdToName,
  userRoleIdToName,
} from '../../utils/reverseMappingConfig';

const API_ENDPOINT = '/settings/api-keys/page/';
const API_METHOD = 'get';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

type TApiKeys = ResponseTypesByStatus['200']['api_keys'];
type TSetApiKeys = React.Dispatch<React.SetStateAction<TApiKeys>>;
type TApiKeyScopeIds = {
  [key: string]: Set<number>;
};
type TSetApiKeyScopeIds = React.Dispatch<React.SetStateAction<TApiKeyScopeIds>>;
type ScopeID = number;

const loadingApiKeyName = 'loading...';

async function handleAddApiKeyScope(
  scopeId: ScopeID,
  apiKey: components['schemas']['ApiKey'],
  setApiKeyScopeIds: TSetApiKeyScopeIds,
  toastContext: ToastContextType,
  authContext: AuthContextType
) {
  const scopeName = scopeIdToName[scopeId];

  let toastId = toastContext.makePending({
    message: `Adding ${scopeName} to ${apiKey.name}`,
  });

  setApiKeyScopeIds((prev) => {
    const updatedSet = new Set(prev[apiKey.id]);
    updatedSet.add(scopeId);
    return {
      ...prev,
      [apiKey.id]: updatedSet,
    };
  });

  const { data, response } = await postApiKeyScope(
    authContext,
    apiKey.id,
    scopeId
  );
  if (response.status === 204) {
    toastContext.update(toastId, {
      message: `Added ${scopeName} to ${apiKey.name}`,
      type: 'success',
    });
  } else {
    toastContext.update(toastId, {
      message: `Error adding ${scopeName} to ${apiKey.name}`,
      type: 'error',
    });
    setApiKeyScopeIds((prev) => {
      const updatedSet = new Set(prev[apiKey.id]);
      updatedSet.delete(scopeId);
      return {
        ...prev,
        [apiKey.id]: updatedSet,
      };
    });
  }
}

async function handleDeleteApiKeyScope(
  scopeId: ScopeID,
  apiKey: components['schemas']['ApiKey'],
  setApiKeyScopeIds: TSetApiKeyScopeIds,
  toastContext: ToastContextType,
  authContext: AuthContextType
) {
  const scopeName = scopeIdToName[scopeId];

  let toastId = toastContext.makePending({
    message: `Removing ${scopeName} from ${apiKey.name}`,
  });

  setApiKeyScopeIds((prev) => {
    const updatedSet = new Set(prev[apiKey.id]);
    updatedSet.delete(scopeId);
    return {
      ...prev,
      [apiKey.id]: updatedSet,
    };
  });

  const { data, response } = await deleteApiKeyScope(
    authContext,
    apiKey.id,
    scopeId
  );

  if (response.status === 204) {
    toastContext.update(toastId, {
      message: `Removed ${scopeName} from ${apiKey.name}`,
      type: 'success',
    });
  } else {
    toastContext.update(toastId, {
      message: `Error removing ${scopeName} from ${apiKey.name}`,
      type: 'error',
    });
    setApiKeyScopeIds((prev) => {
      const updatedSet = new Set(prev[apiKey.id]);
      updatedSet.add(scopeId);
      return {
        ...prev,
        [apiKey.id]: updatedSet,
      };
    });
  }
}

interface ApiKeyScopeRowProps {
  scopeId: ScopeID;
  apiKey: components['schemas']['ApiKey'];
  apiKeyScopeIds: TApiKeyScopeIds;
  setApiKeyScopeIds: TSetApiKeyScopeIds;
  toastContext: ToastContextType;
  authContext: AuthContextType;
}

function ApiKeyScopeRow({
  scopeId,
  apiKey,
  apiKeyScopeIds,
  setApiKeyScopeIds,
  toastContext,
  authContext,
}: ApiKeyScopeRowProps) {
  const [loading, setLoading] = useState<boolean>(false);

  async function handleToggle() {
    setLoading(true);

    if (apiKeyScopeIds[apiKey.id].has(scopeId)) {
      // was on, now turning off
      await handleDeleteApiKeyScope(
        scopeId,
        apiKey,
        setApiKeyScopeIds,
        toastContext,
        authContext
      );
    } else {
      // was off, now turning on
      await handleAddApiKeyScope(
        scopeId,
        apiKey,
        setApiKeyScopeIds,
        toastContext,
        authContext
      );
    }
    setLoading(false);
  }

  return (
    <div
      className="flex flex-row items-center space-x-1"
      key={`${apiKey.id}-${scopeId}`}
    >
      <Toggle1
        onClick={(e) => {
          e.stopPropagation();
          handleToggle();
        }}
        state={apiKeyScopeIds[apiKey.id].has(scopeId)}
        disabled={loading}
      />

      <p>{scopeIdToName[scopeId]}</p>
    </div>
  );
}

interface ApiKeyCodeModalProps {
  authContext: AuthContextType;
  apiKey: components['schemas']['ApiKey'];
}

function ApiKeyCodeModal({ authContext, apiKey }: ApiKeyCodeModalProps) {
  const [jwt, setJwt] = useState<string>('loading...');
  const [copySuccess, setCopySuccess] = useState<boolean>(false);

  useEffect(() => {
    handleGetApiKeyJWT();
  }, []);

  async function handleGetApiKeyJWT() {
    const { data, response } = await getApiKeyJWT(authContext, apiKey.id);

    if (response.status === 200) {
      const apiData = data as GetApiKeyJWTResponseTypes['200'];
      setJwt(apiData.jwt);
    }
  }

  const handleCopyToClipboard = () => {
    navigator.clipboard.writeText(jwt).then(
      () => {
        setCopySuccess(true);
      },
      (err) => {
        console.error('Failed to copy text: ', err);
      }
    );
  };

  return (
    <div id="api-key-code" className="flex flex-col space-y-4">
      <div className="overflow-x-auto overflow-y-clip">
        <h3 className="break-words">{apiKey.name}</h3>
      </div>
      <Card1>
        <div>
          <code className="break-words">{jwt}</code>
        </div>
      </Card1>
      <div className="h-[2rem] flex flex-col justify-center items-center">
        {copySuccess && <p>Copied to clipboard</p>}
      </div>
      <div className="flex flex-row justify-center">
        <Button1
          onClick={(e) => {
            handleCopyToClipboard();
          }}
        >
          Copy API Key
        </Button1>
      </div>
    </div>
  );
}

interface ApiKeyRowProps {
  apiKeyId: components['schemas']['ApiKey']['id'];
  apiKeys: TApiKeys;
  setApiKeys: TSetApiKeys;
  apiKeyScopeIds: TApiKeyScopeIds;
  setApiKeyScopeIds: TSetApiKeyScopeIds;
  toastContext: ToastContextType;
  authContext: AuthContextType;
  globalModalsContext: GlobalModalsContextType;
  checkConfirmation: ReturnType<
    typeof useConfirmationModal
  >['checkConfirmation'];
}

function ApiKeyRow({
  apiKeyId,
  apiKeys,
  setApiKeys,
  apiKeyScopeIds,
  setApiKeyScopeIds,
  toastContext,
  authContext,
  globalModalsContext,
  checkConfirmation,
}: ApiKeyRowProps) {
  const [isEditing, setIsEditing] = useState(false);
  async function handleDeleteApiKey(apiKeyId: string) {
    let toastId = toastContext.makePending({
      message: `Deleting API Key ${apiKeys[apiKeyId].name}`,
    });

    const apiKeyToDelete = apiKeys[apiKeyId];
    const newApiKeys = { ...apiKeys };
    delete newApiKeys[apiKeyId];
    setApiKeys(newApiKeys);

    const apiKeyScopesToDelete = apiKeyScopeIds[apiKeyId];
    const newApiKeyScopes = { ...apiKeyScopeIds };
    delete newApiKeyScopes[apiKeyId];
    setApiKeyScopeIds(newApiKeyScopes);

    const { data, response } = await deleteApiKey(authContext, apiKeyId);

    if (response.status === 204) {
      const apiData = data as DeleteApiKeyResponseTypes['204'];
      toastContext.update(toastId, {
        message: `Deleted API Key ${apiKeyToDelete.name}`,
        type: 'success',
      });
    } else {
      toastContext.update(toastId, {
        message: `Error deleting API Key ${apiKeyToDelete.name}`,
        type: 'error',
      });
      setApiKeys({ ...apiKeys, [apiKeyId]: apiKeyToDelete });
      setApiKeyScopeIds({
        ...apiKeyScopeIds,
        [apiKeyId]: apiKeyScopesToDelete,
      });
    }
  }

  return (
    <Card1
      onClick={() =>
        setIsEditing((prev) => {
          if (apiKeys[apiKeyId].name !== loadingApiKeyName) {
            return !prev;
          }
        })
      }
      className="flex flex-col cursor-pointer"
    >
      <div className="flex flex-row w-full items-center space-x-2">
        <span>
          {isEditing ? <IoChevronDownOutline /> : <IoChevronForwardOutline />}
        </span>
        <div className="flex flex-col flex-1 overflow-x-auto">
          <h3 className="mb-4 ml-4 text-left break-words">
            <code>{apiKeys[apiKeyId].name}</code>
          </h3>
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
        <div className="flex flex-col flex-shrink-0 space-y-2">
          <Button1
            className="flex-shrink-0"
            onClick={(e) => {
              e.stopPropagation();
              globalModalsContext.setModal({
                component: (
                  <ApiKeyCodeModal
                    authContext={authContext}
                    apiKey={apiKeys[apiKeyId]}
                  />
                ),
                className: 'max-w-[400px] w-full',
              });
            }}
          >
            View Key
          </Button1>
          <Button2
            onClick={(e) => {
              e.stopPropagation();
              checkConfirmation(
                {
                  title: 'Delete API Key?',
                  confirmText: 'Delete',
                  message: `Are you sure you want to delete the API Key ${apiKeys[apiKeyId].name}?`,
                  onConfirm: () => {
                    handleDeleteApiKey(apiKeyId);
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
          {config['user_role_scopes'][
            userRoleIdToName[authContext.state.user.user_role_id]
          ].map((user_role_scope) => (
            <ApiKeyScopeRow
              key={user_role_scope}
              scopeId={config['scope_name_mapping'][user_role_scope]}
              apiKey={apiKeys[apiKeyId]}
              apiKeyScopeIds={apiKeyScopeIds}
              toastContext={toastContext}
              setApiKeyScopeIds={setApiKeyScopeIds}
              authContext={authContext}
            />
          ))}
        </div>
      )}
    </Card1>
  );
}

interface AddApiKeyProps {
  authContext: AuthContextType;
  toastContext: ToastContextType;
  globalModalsContext: GlobalModalsContextType;
  setApiKeys: TSetApiKeys;
  setApiKeyScopeIds: TSetApiKeyScopeIds;
}

function AddApiKey({
  authContext,
  toastContext,
  globalModalsContext,
  setApiKeys,
  setApiKeyScopeIds,
}: AddApiKeyProps) {
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

  async function addApiKey(event: React.FormEvent) {
    event.preventDefault();
    globalModalsContext.setModal(null);

    let toastId = toastContext.makePending({
      message: 'Creating API Key...',
    });

    // make a random 16 character string
    const tempId = Math.random().toString();

    const tempApiKey: PostApiKeyResponseTypes['200'] = {
      id: tempId,
      user_id: authContext.state.user.id,
      issued: new Date().toISOString(),
      name: loadingApiKeyName,
      expiry: new Date(expiry['value']).toISOString(),
    };

    setApiKeys((prevApiKeys) => ({
      ...prevApiKeys,
      [tempId]: tempApiKey,
    }));
    setApiKeyScopeIds((prev) => ({ ...prev, [tempId]: new Set() }));

    const { data, response } = await postApiKey(authContext, {
      expiry: new Date(expiry['value']).toISOString(),
      name: name['value'],
    });

    if (response.status === 200) {
      const apiData = data as PostApiKeyResponseTypes['200'];
      toastContext.update(toastId, {
        message: `Created API Key ${apiData.name}`,
        type: 'success',
      });

      setApiKeys((prevApiKeys) => {
        const newApiKeys = { ...prevApiKeys };
        delete newApiKeys[tempId];
        newApiKeys[apiData.id] = apiData;
        return newApiKeys;
      });
      setApiKeyScopeIds((prev) => {
        const newApiKeyScopes = { ...prev };
        delete newApiKeyScopes[tempId];
        newApiKeyScopes[apiData.id] = new Set();
        return newApiKeyScopes;
      });
    } else {
      toastContext.update(toastId, {
        message: 'Error creating API Key',
        type: 'error',
      });

      setApiKeys((prevApiKeys) => {
        const newApiKeys = { ...prevApiKeys };
        delete newApiKeys[tempId];
        return newApiKeys;
      });
      setApiKeyScopeIds((prev) => {
        const newApiKeyScopes = { ...prev };
        delete newApiKeyScopes[tempId];
        return newApiKeyScopes;
      });
    }
  }

  return (
    <div id="add-api-key">
      <form onSubmit={addApiKey} className="flex flex-col space-y-4">
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
                openapi_schema.components.schemas.ApiKeyCreate.properties.name
                  .minLength
              }
              maxLength={
                openapi_schema.components.schemas.ApiKeyCreate.properties.name
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

interface ApiKeysProps {
  authContext: AuthContextType;
  toastContext: ToastContextType;
}

function ApiKeys({ authContext, toastContext }: ApiKeysProps): JSX.Element {
  const globalModalsContext = useContext(GlobalModalsContext);
  const { checkConfirmation } = useConfirmationModal();

  const [apiKeys, setApiKeys] = useState<TApiKeys>({});
  const [apiKeyScopeIds, setApiKeyScopeIds] = useState<TApiKeyScopeIds>({});

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
      setApiKeys(data.api_keys);

      const transformedScopes: TApiKeyScopeIds = {};
      for (const key in data.api_key_scope_ids) {
        transformedScopes[key] = new Set(data.api_key_scope_ids[key]);
      }
      setApiKeyScopeIds(transformedScopes);
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
                    <AddApiKey
                      authContext={authContext}
                      toastContext={toastContext}
                      globalModalsContext={globalModalsContext}
                      setApiKeys={setApiKeys}
                      setApiKeyScopeIds={setApiKeyScopeIds}
                    />
                  ),
                  className: 'max-w-[350px] w-full',
                  key: 'modal-make-api-key',
                });
              }}
            >
              Add API Key
            </Button1>
          </div>
          <div className="flex flex-col space-y-4">
            {Object.keys(apiKeys).map((apiKeyId) => (
              <ApiKeyRow
                key={apiKeyId}
                apiKeyId={apiKeyId}
                apiKeys={apiKeys}
                setApiKeys={setApiKeys}
                apiKeyScopeIds={apiKeyScopeIds}
                setApiKeyScopeIds={setApiKeyScopeIds}
                toastContext={toastContext}
                authContext={authContext}
                globalModalsContext={globalModalsContext}
                checkConfirmation={checkConfirmation}
              />
            ))}
          </div>
        </>
      )}
    </>
  );
}

export { ApiKeys };
