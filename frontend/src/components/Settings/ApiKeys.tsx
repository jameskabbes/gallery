import React, { useContext, useEffect, useRef, useState } from 'react';
import {
  ValidatedInputState,
  ToastContextType,
  ExtractResponseTypes,
  AuthContextType,
  defaultValidatedInputState,
  GlobalModalsContextType,
  OrderByState,
  ArrayElement,
} from '../../types';
import { useApiCall } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import {
  deleteApiKey,
  DeleteApiKeyResponses,
} from '../../services/api/deleteApiKey';

import { postApiKey, PostApiKeyResponses } from '../../services/api/postApiKey';

import { postApiKeyScope } from '../../services/api/postApiKeyScope';
import { deleteApiKeyScope } from '../../services/api/deleteApiKeyScope';

import { GlobalModalsContext } from '../../contexts/GlobalModals';
import { useConfirmationModal } from '../../utils/useConfirmationModal';

import { CiClock2 } from 'react-icons/ci';
import {
  IoCaretForward,
  IoEllipsisHorizontalCircle,
  IoEye,
  IoEyeOutline,
  IoHourglassOutline,
  IoPencil,
  IoPencilOutline,
  IoTrash,
  IoTrashOutline,
} from 'react-icons/io5';
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
  GetApiKeyJwtResponses,
} from '../../services/api/getApiKeyJwt';
import config from '../../../../config.json';
import {
  scopeIdToName,
  userRoleIdToName,
} from '../../utils/reverseMappingConfig';
import { useValidatedInput } from '../../utils/useValidatedInput';
import { isApiKeyAvailable } from '../../services/api/getIsApiKeyAvailable';
import { CheckOrX } from '../Form/CheckOrX';
import {
  getApiKeys,
  GetApiKeysResponses,
  QueryParams,
} from '../../services/api/getApiKeys';
import {
  IoCaretUp,
  IoCaretDown,
  IoArrowForwardSharp,
  IoArrowBackSharp,
  IoEllipsisHorizontal,
} from 'react-icons/io5';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { Loader1 } from '../Utils/Loader';
import { Surface } from '../Utils/Surface';
import { patchApiKey } from '../../services/api/patchApiKey';
import { useClickOutside } from '../../utils/useClickOutside';
import { Modal } from '../Modal/Modal';

type ScopeID = number;
type TApiKey = components['schemas']['ApiKeyPrivate'];
type TApiKeys = Record<TApiKey['id'], TApiKey>;
type TApiKeyScopeIds = {
  [key: TApiKey['id']]: Set<ScopeID>;
};
type TJwt = GetApiKeyJwtResponses['200']['jwt'];
type TModifyApiKeyScopeFunc = (
  apiKey: TApiKey,
  scopeId: ScopeID
) => Promise<void>;
type TAddApiKeyFunc = (
  apiKeyCreate: Parameters<typeof postApiKey>[1]
) => Promise<boolean>;
type TUpdateApiKeyFunc = (
  apiKeyId: Parameters<typeof patchApiKey>[1],
  apiKeyUpdate: Parameters<typeof patchApiKey>[2]
) => Promise<boolean>;

interface ApiKeyCodeModalProps {
  authContext: AuthContextType;
  apiKey: TApiKey;
}

function ApiKeyCodeModal({ apiKey, authContext }: ApiKeyCodeModalProps) {
  const [loading, setLoading] = useState<boolean>(true);
  const [jwt, setJwt] = useState<TJwt>(null);
  const [copySuccess, setCopySuccess] = useState<boolean>(false);

  async function fetchJwt() {
    setLoading(true);
    const { data, status } = await getApiKeyJWT(authContext, apiKey.id);
    if (status === 200) {
      const apiData = data as GetApiKeyJwtResponses['200'];
      setJwt(apiData.jwt);
    } else {
      return null;
    }
    setLoading(false);
  }

  useEffect(() => {
    fetchJwt();
  }, []);

  return (
    <div id="api-key-code" className="flex flex-col space-y-4">
      <Card1>
        <div>
          {loading ? (
            <Loader1 />
          ) : jwt ? (
            <code className="break-words">{jwt}</code>
          ) : (
            <p>Error generating code</p>
          )}
        </div>
      </Card1>
      <div className="h-[2rem] flex flex-col justify-center items-center">
        {copySuccess && <p>Copied to clipboard</p>}
      </div>
      <div className="flex flex-row justify-center">
        <Button1
          onClick={(e) => {
            navigator.clipboard.writeText(jwt).then(
              () => {
                setCopySuccess(true);
              },
              (err) => {
                console.error('Failed to copy text: ', err);
              }
            );
          }}
        >
          Copy API Key
        </Button1>
      </div>
    </div>
  );
}

interface UpdateApiKeyProps {
  authContext: AuthContextType;
  apiKeyId: TApiKey['id'];
  apiKeys: TApiKeys;
  updateApiKeyFunc: TUpdateApiKeyFunc;
}

function UpdateApiKey({
  authContext,
  apiKeyId,
  apiKeys,
  updateApiKeyFunc,
}: UpdateApiKeyProps) {
  interface ValidatedApiKeyAvailable {
    name: ValidatedInputState<string>;
  }

  const [name, setName] = useState<ValidatedInputState<string>>({
    ...defaultValidatedInputState<string>(apiKeys[apiKeyId].name),
  });
  const [nameModified, setNameModified] = useState<boolean>(false);
  const [expiry, setExpiry] = useState<ValidatedInputState<Date>>({
    ...defaultValidatedInputState<Date>(new Date(apiKeys[apiKeyId].expiry)),
  });
  const [expiryModified, setExpiryModified] = useState<boolean>(false);
  const [modified, setModified] = useState<boolean>(false);

  const [apiKeyAvailable, setApiKeyAvailable] = useState<
    ValidatedInputState<ValidatedApiKeyAvailable>
  >({
    ...defaultValidatedInputState<ValidatedApiKeyAvailable>({
      name: name,
    }),
  });

  useEffect(() => {
    setNameModified(apiKeys[apiKeyId].name !== name.value);
  }, [name.value, apiKeys]);
  useEffect(() => {
    setExpiryModified(
      new Date(apiKeys[apiKeyId].expiry).getTime() !== expiry.value.getTime()
    );
  }, [expiry.value, apiKeys]);
  useEffect(() => {
    setModified(nameModified || expiryModified);
  }, [nameModified, expiryModified]);

  useValidatedInput<ValidatedApiKeyAvailable>({
    state: apiKeyAvailable,
    setState: setApiKeyAvailable,
    checkAvailability: nameModified,
    checkValidity: true,
    isAvailable: () =>
      isApiKeyAvailable(authContext, {
        name: name.value,
      }),
    isValid: (value) => {
      return value.name.status === 'valid'
        ? { valid: true }
        : { valid: false, message: 'Invalid name' };
    },
  });

  useEffect(() => {
    setApiKeyAvailable((prev) => ({
      ...prev,
      value: {
        name: name,
      },
    }));
  }, [name]);

  return (
    <div id="update-api-key">
      <form
        onSubmit={async (e) => {
          e.preventDefault();
          if (
            await updateApiKeyFunc(apiKeyId, {
              name: nameModified ? name.value : undefined,
              expiry: expiryModified
                ? new Date(expiry.value).toISOString()
                : undefined,
            })
          ) {
          }
        }}
        className="flex flex-col space-y-4"
      >
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
              showStatus={nameModified}
            />
          </section>
          <section>
            <label htmlFor="api-key-expiry">Expiry</label>
            <ValidatedInputDatetimeLocal
              state={expiry}
              setState={setExpiry}
              id="api-key-expiry"
              required={true}
              showStatus={expiryModified}
            />
          </section>
        </fieldset>

        <div className="h-[2rem] flex flex-row justify-center space-x-2 items-center">
          {modified && (
            <>
              <p className="text-center">
                {apiKeyAvailable.status === 'valid'
                  ? 'Available'
                  : apiKeyAvailable.status === 'loading'
                  ? 'Checking'
                  : 'Not available'}
              </p>
              <CheckOrX status={apiKeyAvailable.status} />
            </>
          )}
        </div>
        <div className="flex flex-row space-x-4">
          <Button2
            className="flex-1"
            disabled={!modified}
            onClick={(e) => {
              e.preventDefault();
              setName({
                ...defaultValidatedInputState<string>(apiKeys[apiKeyId].name),
              });
              setExpiry({
                ...defaultValidatedInputState<Date>(
                  new Date(apiKeys[apiKeyId].expiry)
                ),
              });
            }}
          >
            Cancel
          </Button2>
          <Button1
            className="flex-1"
            disabled={apiKeyAvailable.status !== 'valid' || !modified}
            type="submit"
          >
            Submit
          </Button1>
        </div>
      </form>
    </div>
  );
}

interface AddApiKeyProps {
  authContext: AuthContextType;
  addApiKeyFunc: TAddApiKeyFunc;
  globalModalsContext: GlobalModalsContextType;
}

function AddApiKey({
  authContext,
  addApiKeyFunc,
  globalModalsContext,
}: AddApiKeyProps) {
  interface ValidatedApiKeyAvailable {
    name: ValidatedInputState<string>;
  }

  const [name, setName] = useState<ValidatedInputState<string>>({
    ...defaultValidatedInputState<string>(''),
  });
  const [expiry, setExpiry] = useState<ValidatedInputState<Date>>({
    ...defaultValidatedInputState<Date>(
      new Date(new Date().setMonth(new Date().getMonth() + 1))
    ),
  });

  const [apiKeyAvailable, setApiKeyAvailable] = useState<
    ValidatedInputState<ValidatedApiKeyAvailable>
  >({
    ...defaultValidatedInputState<ValidatedApiKeyAvailable>({
      name: name,
    }),
  });

  useValidatedInput<ValidatedApiKeyAvailable>({
    state: apiKeyAvailable,
    setState: setApiKeyAvailable,
    checkAvailability: true,
    checkValidity: true,
    isAvailable: () =>
      isApiKeyAvailable(authContext, {
        name: name.value,
      }),
    isValid: (value) => {
      return value.name.status === 'valid'
        ? { valid: true }
        : { valid: false, message: 'Invalid name' };
    },
  });

  useEffect(() => {
    setApiKeyAvailable((prev) => ({
      ...prev,
      value: {
        name: name,
      },
    }));
  }, [name]);

  return (
    <div id="add-api-key">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (
            addApiKeyFunc({
              expiry: new Date(expiry.value).toISOString(),
              name: name.value,
            })
          ) {
            globalModalsContext.clearModal();
          }
        }}
        className="flex flex-col space-y-4"
      >
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

        <div className="flex flex-row justify-center space-x-2 items-center">
          <p className="text-center">
            {apiKeyAvailable.status === 'valid'
              ? 'Available'
              : apiKeyAvailable.status === 'loading'
              ? 'Checking'
              : 'Not available'}
          </p>
          <CheckOrX status={apiKeyAvailable.status} />
        </div>

        <ButtonSubmit disabled={apiKeyAvailable.status !== 'valid'}>
          Add API Key
        </ButtonSubmit>
      </form>
    </div>
  );
}

interface ApiKeyTableRowScopeProps {
  scopeId: ScopeID;
  apiKey: TApiKey;
  apiKeyScopeIds: TApiKeyScopeIds;
  deleteApiKeyScopeFunc: TModifyApiKeyScopeFunc;
  addApiKeyScopeFunc: TModifyApiKeyScopeFunc;
}

function ApiKeyTableRowScope({
  scopeId,
  apiKey,
  apiKeyScopeIds,
  addApiKeyScopeFunc,
  deleteApiKeyScopeFunc,
}: ApiKeyTableRowScopeProps) {
  const [loading, setLoading] = useState<boolean>(false);
  return (
    <Toggle1
      onClick={async (e) => {
        e.stopPropagation();
        setLoading(true);
        if (apiKeyScopeIds[apiKey.id].has(scopeId)) {
          await deleteApiKeyScopeFunc(apiKey, scopeId);
        } else {
          await addApiKeyScopeFunc(apiKey, scopeId);
        }
        setLoading(false);
      }}
      state={apiKeyScopeIds[apiKey.id].has(scopeId)}
      disabled={loading}
    />
  );
}

interface ApiKeyViewProps {
  apiKeyId: TApiKey['id'];
  apiKeys: TApiKeys;
  authContext: AuthContextType;
  updateApiKeyFunc: TUpdateApiKeyFunc;
  globalModalsContext: GlobalModalsContextType;
}

function ApiKeyView({
  apiKeys,
  apiKeyId,
  authContext,
  updateApiKeyFunc,
  globalModalsContext,
}: ApiKeyViewProps) {
  type Mode = 'code' | 'scopes' | 'edit';

  const modes: Mode[] = ['code', 'scopes', 'edit'];
  const [mode, setMode] = useState<Mode>('code');
  const [apiKeyName, setApiKeyName] = useState<string>(apiKeys[apiKeyId].name);

  useEffect(() => {
    setApiKeyName(apiKeys[apiKeyId].name);
  }, [apiKeys, apiKeyId]);

  useEffect(() => {
    console.log('apikeys changed');
  }, [apiKeys]);

  return (
    <div className="flex flex-col space-y-4">
      <div className="overflow-x-auto overflow-y-clip">
        <h3 className="break-words">{apiKeyName}</h3>
      </div>
      <div className="flex flex-row space-x-4">
        {modes.map((m) => (
          <Button2
            key={m}
            onClick={() => setMode(m)}
            className={`${
              mode === m ? ' border-primary-light dark:border-primary-dark' : ''
            } flex-1 w-16`}
          >
            {m}
          </Button2>
        ))}
      </div>
      {mode === 'code' && (
        <ApiKeyCodeModal apiKey={apiKeys[apiKeyId]} authContext={authContext} />
      )}
      {mode === 'scopes' && <p>scopes</p>}
      {mode === 'edit' && (
        <>
          <UpdateApiKey
            apiKeyId={apiKeyId}
            apiKeys={apiKeys}
            authContext={authContext}
            updateApiKeyFunc={updateApiKeyFunc}
          />
        </>
      )}
    </div>
  );
}

interface ApiKeysProps {
  authContext: AuthContextType;
  toastContext: ToastContextType;
}

const API_ENDPOINT = '/pages/settings/api-keys/';
const API_METHOD = 'get';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

function ApiKeys({ authContext, toastContext }: ApiKeysProps): JSX.Element {
  const globalModalsContext = useContext(GlobalModalsContext);
  const { checkButtonConfirmation } = useConfirmationModal();

  const navigate = useNavigate();
  const query = new URLSearchParams(useLocation().search);

  type QueryParamKey = keyof paths['/api-keys/']['get']['parameters']['query'];
  const queryParameters =
    openapi_schema['paths']['/api-keys/']['get']['parameters'];

  const queryParamObjects: Record<QueryParamKey, any> = queryParameters.reduce(
    (acc, param) => {
      acc[param.name as QueryParamKey] = param;
      return acc;
    },
    {} as Record<QueryParamKey, any>
  );

  const orderByFields = new Set(
    queryParamObjects['order_by'].schema.items.enum as OrderByField[]
  );

  function getLimitFromQuery(limit: string): QueryParams['limit'] {
    if (!limit) {
      return queryParamObjects['limit'].schema.default;
    } else {
      const limitInt = parseInt(limit, 10);
      if (isNaN(limitInt)) {
        return queryParamObjects['limit'].schema.default;
      } else {
        return Math.min(
          queryParamObjects['limit'].schema.maximum,
          Math.max(queryParamObjects['limit'].schema.minimum, limitInt)
        );
      }
    }
  }

  function getOffsetFromQuery(offset: string): QueryParams['offset'] {
    if (!offset) {
      return queryParamObjects['offset'].schema.default;
    } else {
      const offsetInt = parseInt(offset, 10);
      if (isNaN(offsetInt)) {
        return queryParamObjects['offset'].schema.default;
      } else {
        return Math.max(queryParamObjects['offset'].schema.minimum, offsetInt);
      }
    }
  }

  function getOrderByFromQuery(orderBy: string[]): QueryParams['order_by'] {
    return orderBy.filter((field: OrderByField) =>
      orderByFields.has(field)
    ) as QueryParams['order_by'];
  }

  const [limit, setLimit] = useState<QueryParams['limit']>(
    getLimitFromQuery(query.get('limit'))
  );

  const [offset, setOffset] = useState<QueryParams['offset']>(
    getOffsetFromQuery(query.get('offset'))
  );

  const [orderBy, setOrderBy] = useState<QueryParams['order_by']>(
    getOrderByFromQuery(query.getAll('order_by'))
  );

  const [orderByDesc, setOrderByDesc] = useState<QueryParams['order_by_desc']>(
    getOrderByFromQuery(query.getAll('order_by_desc'))
  );

  //   Update URL when state changes
  useEffect(() => {
    const params = new URLSearchParams();
    if (limit !== queryParamObjects['limit'].schema.default)
      params.set('limit', limit.toString());
    if (offset !== queryParamObjects['offset'].schema.default)
      params.set('offset', offset.toString());
    orderBy.forEach((field) => params.append('order_by', field));
    orderByDesc.forEach((field) => params.append('order_by_desc', field));

    const newSearch = params.toString();
    if (newSearch !== location.search) {
      navigate({ search: newSearch });
    }
  }, [limit, offset, orderBy, orderByDesc]);

  const [apiKeyCount, setApiKeyCount] = useState<number>(0);
  const [apiKeys, setApiKeys] = useState<TApiKeys>({});
  const [apiKeyIdIndex, setApiKeyIdIndex] = useState<TApiKey['id'][]>([]);
  const [apiKeyScopeIds, setApiKeyScopeIds] = useState<TApiKeyScopeIds>({});
  const [availableScopeIds, setAvailableScopeIds] = useState<ScopeID[]>([]);

  const [selectedIndex, setSelectedIndex] = useState<number>(null);

  type OrderByField = ArrayElement<
    paths['/api-keys/']['get']['parameters']['query']['order_by']
  >;

  // show the available scopes based on the user's role
  useEffect(() => {
    if (authContext.state.user !== null) {
      setAvailableScopeIds(
        config['user_role_scopes'][
          userRoleIdToName[authContext.state.user.user_role_id]
        ].map((user_role_scope: string) => {
          return config['scope_name_mapping'][user_role_scope];
        })
      );
    }
  }, [authContext]);

  const { data, status, loading, refetch } = useApiCall<
    ResponseTypesByStatus[keyof ResponseTypesByStatus]
  >({
    url: API_ENDPOINT,
    method: API_METHOD,
    params: {
      limit: limit,
      offset: offset,
      order_by: orderBy,
      order_by_desc: orderByDesc,
    },
  });

  const hasMounted = useRef(false);

  // refetch when limit, offset, orderBy, or orderByDesc changes
  useEffect(() => {
    if (hasMounted.current) {
      refetch();
    } else {
      hasMounted.current = true;
    }
  }, [offset, limit, orderBy, orderByDesc]);

  // when data is fetched, update the states
  useEffect(() => {
    if (!loading) {
      if (status === 200) {
        const apiData = data as ResponseTypesByStatus['200'];
        setApiKeys(() => {
          const keys = {};
          for (const apiKey of apiData.api_keys) {
            keys[apiKey.id] = apiKey;
          }
          return keys;
        });
        setApiKeyScopeIds(() => {
          const keys = {};
          for (const apiKey of apiData.api_keys) {
            keys[apiKey.id] = new Set(apiKey.scope_ids);
          }
          return keys;
        });
        setApiKeyIdIndex((prev) => {
          const keys = [];
          for (const apiKey of apiData.api_keys) {
            keys.push(apiKey.id);
          }
          return keys;
        });
        setApiKeyCount(apiData.api_key_count);
      }
    }
  }, [data, status, loading]);

  useEffect(() => {
    if (selectedIndex === null) {
      globalModalsContext.clearModal();
    } else {
      globalModalsContext.setModal({
        contentAdditionalClassName: 'max-w-[400px] w-full',
        children: (
          <ApiKeyView
            apiKeyId={apiKeyIdIndex[selectedIndex]}
            apiKeys={apiKeys}
            authContext={authContext}
            updateApiKeyFunc={updateApiKeyFunc}
            globalModalsContext={globalModalsContext}
          />
        ),
      });
    }
  }, [selectedIndex, apiKeyIdIndex, apiKeys]);

  const addApiKeyScopeFunc: TModifyApiKeyScopeFunc = async (
    apiKey,
    scopeId
  ) => {
    setApiKeyScopeIds((prev) => {
      const updatedSet = new Set(prev[apiKey.id]);
      updatedSet.add(scopeId);
      return {
        ...prev,
        [apiKey.id]: updatedSet,
      };
    });

    const { data, status } = await postApiKeyScope(
      authContext,
      apiKey.id,
      scopeId
    );
    if (status === 200) {
    } else {
      setApiKeyScopeIds((prev) => {
        const updatedSet = new Set(prev[apiKey.id]);
        updatedSet.delete(scopeId);
        return {
          ...prev,
          [apiKey.id]: updatedSet,
        };
      });
    }
  };

  const deleteApiKeyScopeFunc: TModifyApiKeyScopeFunc = async (
    apiKey,
    scopeId
  ) => {
    const scopeName = scopeIdToName[scopeId];

    setApiKeyScopeIds((prev) => {
      const updatedSet = new Set(prev[apiKey.id]);
      updatedSet.delete(scopeId);
      return {
        ...prev,
        [apiKey.id]: updatedSet,
      };
    });

    const { data, status } = await deleteApiKeyScope(
      authContext,
      apiKey.id,
      scopeId
    );

    if (status === 204) {
    } else {
      setApiKeyScopeIds((prev) => {
        const updatedSet = new Set(prev[apiKey.id]);
        updatedSet.add(scopeId);
        return {
          ...prev,
          [apiKey.id]: updatedSet,
        };
      });
    }
  };

  const addApiKeyFunc: TAddApiKeyFunc = async (apiKeyCreate) => {
    let toastId = toastContext.makePending({
      message: 'Creating API Key...',
    });

    const { data, status } = await postApiKey(authContext, apiKeyCreate);

    if (status === 200) {
      const apiData = data as PostApiKeyResponses['200'];
      toastContext.update(toastId, {
        message: `Created API Key ${apiData.name}`,
        type: 'success',
      });
      refetch();
      return true;
    } else {
      toastContext.update(toastId, {
        message: 'Error creating API Key',
        type: 'error',
      });
      return false;
    }
  };

  const updateApiKeyFunc: TUpdateApiKeyFunc = async (
    apiKeyId,
    apiKeyUpdate
  ) => {
    let toastId = toastContext.makePending({
      message: 'Updating API Key...',
    });

    const { data, status } = await patchApiKey(
      authContext,
      apiKeyId,
      apiKeyUpdate
    );

    if (status === 200) {
      const apiData = data as PostApiKeyResponses['200'];
      toastContext.update(toastId, {
        message: `Created API Key ${apiData.name}`,
        type: 'success',
      });
      refetch();
      return true;
    } else {
      toastContext.update(toastId, {
        message: 'Error creating API Key',
        type: 'error',
      });
      return false;
    }
  };

  function handleDelete(apiKey: TApiKey) {
    checkButtonConfirmation(
      {
        title: 'Delete API Key?',
        confirmText: 'Delete',
        message: `Are you sure you want to delete the API Key ${apiKey.name}?`,
        onConfirm: async () => {
          let toastId = toastContext.makePending({
            message: `Deleting API Key ${apiKey.name}`,
          });

          const { data, status } = await deleteApiKey(authContext, apiKey.id);

          if (status === 204) {
            const apiData = data as DeleteApiKeyResponses['204'];
            toastContext.update(toastId, {
              message: `Deleted API Key ${apiKey.name}`,
              type: 'success',
            });
            refetch();
          } else {
            toastContext.update(toastId, {
              message: `Error deleting API Key ${apiKey.name}`,
              type: 'error',
            });
          }
        },
        onCancel: () => {},
      },
      {
        key: 'delete-api-key',
      }
    );
  }

  if (authContext.state.user !== null) {
    return (
      <>
        <div className="flex flex-row space-x-4 mb-4">
          <h2>API Keys</h2>
        </div>
        <Card1>
          <div className="flex flex-row justify-between items-center space-x-2">
            <div className="flex flex-row items-center space-x-4">
              <Button1
                onClick={() => {
                  globalModalsContext.setModal({
                    children: (
                      <AddApiKey
                        addApiKeyFunc={addApiKeyFunc}
                        authContext={authContext}
                        globalModalsContext={globalModalsContext}
                      />
                    ),
                    contentAdditionalClassName: 'max-w-[350px] w-full',
                    modalKey: 'modal-make-api-key',
                  });
                }}
              >
                Add API Key
              </Button1>
            </div>
            {apiKeyIdIndex.length < apiKeyCount && (
              <div className="flex flex-row items-center space-x-1">
                {loading ? (
                  <Loader1 />
                ) : (
                  <p>
                    {loading ? 'x' : offset + 1}-
                    {loading ? 'x' : offset + Object.keys(apiKeys).length} of{' '}
                    {loading ? 'x' : apiKeyCount}
                  </p>
                )}
                <button
                  disabled={offset === 0 || loading}
                  onClick={() =>
                    setOffset((prev) =>
                      Math.max(
                        queryParamObjects['offset'].schema.minimum,
                        prev - limit
                      )
                    )
                  }
                >
                  <IoArrowBackSharp
                    className={offset === 0 || loading ? 'opacity-50' : ''}
                  />
                </button>
                <button
                  onClick={() => setOffset((prev) => prev + limit)}
                  disabled={offset + limit >= apiKeyCount || loading}
                >
                  <IoArrowForwardSharp
                    className={
                      offset + limit >= apiKeyCount || loading
                        ? 'opacity-50'
                        : ''
                    }
                  />
                </button>
              </div>
            )}
          </div>

          <div className="overflow-x-auto mt-4 overflow-y-visible">
            <table className="min-w-full">
              <thead className="text-left">
                <tr>
                  {['name', 'issued', 'expiry'].map((field) => (
                    <th key={field}>
                      {(() => {
                        const typedField = field as OrderByField; // Type assertion
                        let orderByState: OrderByState = 'off';

                        // get index of field in orderBy
                        const orderByIndex = orderBy.indexOf(typedField);
                        if (orderByIndex !== -1) {
                          orderByState = 'asc';
                        }
                        const orderByDescIndex =
                          orderByDesc.indexOf(typedField);
                        if (orderByDescIndex !== -1) {
                          orderByState = 'desc';
                        }

                        return (
                          <>
                            {orderByFields.has(typedField) ? (
                              <div
                                className="flex flex-row items-center surface-hover cursor-pointer pl-2"
                                onClick={() => {
                                  if (orderByState === 'off') {
                                    setOrderBy((prev) => {
                                      const updated = [...prev, typedField];
                                      return updated;
                                    });
                                  } else if (orderByState === 'asc') {
                                    setOrderByDesc((prev) => {
                                      const updated = [...prev, typedField];
                                      return updated;
                                    });
                                  } else if (orderByState === 'desc') {
                                    setOrderBy((prev) => {
                                      const updated = prev.filter(
                                        (item) => item !== typedField
                                      );
                                      return updated;
                                    });
                                    setOrderByDesc((prev) => {
                                      const updated = prev.filter(
                                        (item) => item !== typedField
                                      );
                                      return updated;
                                    });
                                  }
                                }}
                              >
                                {typedField}
                                {orderByState === 'off' ? (
                                  <IoCaretForward />
                                ) : (
                                  <>
                                    {orderByState === 'asc' ? (
                                      <IoCaretDown />
                                    ) : (
                                      <IoCaretUp />
                                    )}
                                    {(() => {
                                      const index = orderBy.indexOf(typedField);
                                      return index + 1;
                                    })()}
                                  </>
                                )}
                              </div>
                            ) : (
                              typedField
                            )}
                          </>
                        );
                      })()}
                    </th>
                  ))}
                  {availableScopeIds.map((scopeId) => (
                    <th key={scopeId}>{scopeIdToName[scopeId]}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {apiKeyIdIndex.map((apiKeyId, index) => (
                  <Surface key={apiKeyId}>
                    <tr
                      className="surface-hover cursor-pointer border-[1px]"
                      onClick={() => {
                        setSelectedIndex(index);
                      }}
                    >
                      <td className="px-2 py-1">{apiKeys[apiKeyId].name}</td>
                      <td className="px-2 py-1">
                        {new Date(apiKeys[apiKeyId].issued).toLocaleString()}
                      </td>
                      <td className="px-2 py-1">
                        {new Date(apiKeys[apiKeyId].expiry).toLocaleString()}
                      </td>
                      {availableScopeIds.map((scopeId) => (
                        <td key={scopeId} className="px-2 py-1">
                          <ApiKeyTableRowScope
                            scopeId={scopeId}
                            apiKey={apiKeys[apiKeyId]}
                            apiKeyScopeIds={apiKeyScopeIds}
                            addApiKeyScopeFunc={addApiKeyScopeFunc}
                            deleteApiKeyScopeFunc={deleteApiKeyScopeFunc}
                          />
                        </td>
                      ))}
                    </tr>
                  </Surface>
                ))}
              </tbody>
            </table>
          </div>
        </Card1>
      </>
    );
  }
}

export { ApiKeys };
