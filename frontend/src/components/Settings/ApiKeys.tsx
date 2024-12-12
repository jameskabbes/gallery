import React, { useContext, useEffect, useState } from 'react';
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
} from 'react-icons/io5';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { Loader1 } from '../Utils/Loader';

type ScopeID = number;
type TApiKey = components['schemas']['ApiKeyPrivate'];
type TApiKeys = Record<TApiKey['id'], TApiKey>;
type TSetApiKeys = React.Dispatch<React.SetStateAction<TApiKeys>>;
type TApiKeyScopeIds = {
  [key: TApiKey['id']]: Set<ScopeID>;
};
type TSetApiKeyScopeIds = React.Dispatch<React.SetStateAction<TApiKeyScopeIds>>;

const loadingApiKeyName = 'loading...';

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
    const { data, status } = await getApiKeyJWT(authContext, apiKey.id);

    if (status === 200) {
      const apiData = data as GetApiKeyJwtResponses['200'];
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

  interface ValidatedApiKeyAvailable {
    name: ValidatedInputState<string>;
  }

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

  async function addApiKey(event: React.FormEvent) {
    event.preventDefault();
    globalModalsContext.setModal(null);

    let toastId = toastContext.makePending({
      message: 'Creating API Key...',
    });

    // make a random 16 character string
    const tempId = Math.random().toString();

    const tempApiKey: TApiKey = {
      id: tempId,
      user_id: authContext.state.user.id,
      issued: new Date().toISOString(),
      name: loadingApiKeyName,
      expiry: new Date(expiry['value']).toISOString(),
      scope_ids: [],
    };

    setApiKeys((prevApiKeys) => ({
      ...prevApiKeys,
      [tempId]: tempApiKey,
    }));
    setApiKeyScopeIds((prev) => ({ ...prev, [tempId]: new Set() }));

    const { data, status } = await postApiKey(authContext, {
      expiry: new Date(expiry['value']).toISOString(),
      name: name['value'],
    });

    if (status === 200) {
      const apiData = data as PostApiKeyResponses['200'];
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

  const { data, status } = await postApiKeyScope(
    authContext,
    apiKey.id,
    scopeId
  );
  if (status === 200) {
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
  apiKey: TApiKey,
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

  const { data, status } = await deleteApiKeyScope(
    authContext,
    apiKey.id,
    scopeId
  );

  if (status === 204) {
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

interface ApiKeyTableRowScopeProps {
  scopeId: ScopeID;
  apiKey: TApiKey;
  apiKeyScopeIds: TApiKeyScopeIds;
  setApiKeyScopeIds: TSetApiKeyScopeIds;
  toastContext: ToastContextType;
  authContext: AuthContextType;
}

function ApiKeyTableRowScope({
  scopeId,
  apiKey,
  apiKeyScopeIds,
  setApiKeyScopeIds,
  toastContext,
  authContext,
}: ApiKeyTableRowScopeProps) {
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
    <Toggle1
      onClick={(e) => {
        e.stopPropagation();
        handleToggle();
      }}
      state={apiKeyScopeIds[apiKey.id].has(scopeId)}
      disabled={loading}
    />
  );
}

interface ApiKeyTableRowProps {
  apiKey: TApiKey;
  apiKeyScopeIds: TApiKeyScopeIds;
  availableScopeIds: ScopeID[];
  setApiKeyScopeIds: TSetApiKeyScopeIds;
  toastContext: ToastContextType;
  authContext: AuthContextType;
}

function ApiKeyTableRow({
  apiKey,
  apiKeyScopeIds,
  availableScopeIds,
  setApiKeyScopeIds,
  toastContext,
  authContext,
}: ApiKeyTableRowProps) {
  return (
    <tr>
      <td>{apiKey.name}</td>
      <td>
        {new Date(apiKey.issued).toLocaleString('en-US', {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
          hour: 'numeric',
          minute: 'numeric',
        })}
      </td>
      <td>
        {new Date(apiKey.expiry).toLocaleString('en-US', {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
          hour: 'numeric',
          minute: 'numeric',
        })}
      </td>
      {availableScopeIds.map((scopeId) => (
        <td key={scopeId}>
          <ApiKeyTableRowScope
            scopeId={scopeId}
            apiKey={apiKey}
            apiKeyScopeIds={apiKeyScopeIds}
            setApiKeyScopeIds={setApiKeyScopeIds}
            toastContext={toastContext}
            authContext={authContext}
          />
        </td>
      ))}
    </tr>
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
  const [fetchTrigger, setFetchTrigger] = useState<number>(0);
  const [apiKeyIdIndex, setApiKeyIdIndex] = useState<TApiKey['id'][]>([]);
  const [apiKeyScopeIds, setApiKeyScopeIds] = useState<TApiKeyScopeIds>({});
  const [availableScopeIds, setAvailableScopeIds] = useState<ScopeID[]>([]);

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

  const { data, status, loading } = useApiCall<
    ResponseTypesByStatus[keyof ResponseTypesByStatus]
  >(
    {
      url: API_ENDPOINT,
      method: API_METHOD,
      params: {
        limit: limit,
        offset: offset,
        order_by: orderBy,
        order_by_desc: orderByDesc,
      },
    },
    [fetchTrigger]
  );

  useEffect(() => {
    setFetchTrigger((prev) => prev + 1);
  }, [offset, limit, orderBy, orderByDesc]);

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

  async function handleDeleteApiKey(index: number) {
    const apiKeyToDelete = apiKeys[apiKeyIdIndex[index]];

    let toastId = toastContext.makePending({
      message: `Deleting API Key ${apiKeyToDelete.name}`,
    });

    // delete the api key from showing up
    const newApiKeyIdIndex = [...apiKeyIdIndex];
    newApiKeyIdIndex.splice(index, 1);
    setApiKeyIdIndex(newApiKeyIdIndex);

    const { data, status } = await deleteApiKey(authContext, apiKeyToDelete.id);

    if (status === 204) {
      const apiData = data as DeleteApiKeyResponses['204'];
      toastContext.update(toastId, {
        message: `Deleted API Key ${apiKeyToDelete.name}`,
        type: 'success',
      });

      // now, actually delete the api key from the state
      setApiKeys((prev) => {
        const updated = { ...prev };
        delete updated[apiKeyToDelete.id];
        return updated;
      });
      setApiKeyScopeIds((prev) => {
        const updated = { ...prev };
        delete updated[apiKeyToDelete.id];
        return updated;
      });
    } else {
      toastContext.update(toastId, {
        message: `Error deleting API Key ${apiKeyToDelete.name}`,
        type: 'error',
      });
      // re-add the api key to the index state
      const newApiKeyIdIndex = [...apiKeyIdIndex];
      newApiKeyIdIndex.splice(index, 0, apiKeyToDelete.id);
      setApiKeyIdIndex(newApiKeyIdIndex);
    }
  }
  {
    /* <Button1
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
            </Button1> */
  }

  //   <Button2
  //     onClick={(e) => {
  //       e.stopPropagation();
  //       checkButtonConfirmation(
  //         {
  //           title: 'Delete API Key?',
  //           confirmText: 'Delete',
  //           message: `Are you sure you want to delete the API Key ${apiKeys[apiKeyId].name}?`,
  //           onConfirm: () => {
  //             handleDeleteApiKey(apiKeyId);
  //           },
  //           onCancel: () => {},
  //         },
  //         {
  //           key: 'delete-api-key',
  //         }
  //       );
  //     }}
  //   >
  //     <span className="text-error-500">Delete</span>
  //   </Button2>;

  if (authContext.state.user !== null) {
    return (
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
        <table>
          <thead>
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
                    const orderByDescIndex = orderByDesc.indexOf(typedField);
                    if (orderByDescIndex !== -1) {
                      orderByState = 'desc';
                    }

                    return (
                      <>
                        {orderByFields.has(typedField) ? (
                          <Button2
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
                            <div className="flex flex-row items-center">
                              {typedField}
                              {orderByState !== 'off' && (
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
                          </Button2>
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
            {apiKeyIdIndex.map((apiKeyId) => (
              <ApiKeyTableRow
                key={apiKeyId}
                apiKey={apiKeys[apiKeyId]}
                apiKeyScopeIds={apiKeyScopeIds}
                availableScopeIds={availableScopeIds}
                setApiKeyScopeIds={setApiKeyScopeIds}
                toastContext={toastContext}
                authContext={authContext}
              />
            ))}
          </tbody>
        </table>
        {loading && <Loader1 />}
        <div className="flex flex-row">
          <button
            disabled={offset === 0}
            onClick={() =>
              setOffset((prev) =>
                Math.max(
                  queryParamObjects['offset'].schema.minimum,
                  prev - limit
                )
              )
            }
          >
            <IoArrowBackSharp />
          </button>
          <button
            onClick={() => setOffset((prev) => prev + limit)}
            disabled={offset + limit >= apiKeyCount}
          >
            <IoArrowForwardSharp />
          </button>
          <p>
            {loading ? 'x' : offset + 1}-
            {loading ? 'x' : offset + Object.keys(apiKeys).length} of{' '}
            {loading ? 'x' : apiKeyCount}
          </p>
        </div>
      </>
    );
  }
}

export { ApiKeys };
