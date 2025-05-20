import React, { useContext, useEffect, useRef, useState } from 'react';
import {
  ValidatedInputState,
  ToastContextType,
  AuthContextType,
  defaultValidatedInputState,
  ModalsContextType,
  OrderByState,
  ArrayElement,
  ModalType,
  ModalUpdateType,
  GetElementTypeFromArray,
} from '../../types';
import { useApiCall } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import {
  deleteApiKey,
  postApiKey,
  postApiKeyScope,
  deleteApiKeyScope,
  getApiKeyJwt,
  getIsApiKeyAvailable,
  patchApiKey,
  getApiKeysSettingsPage,
} from '../../services/apiServices';

import { ModalsContext } from '../../contexts/Modals';
import { useConfirmationModal } from '../../utils/useConfirmationModal';
import { IoCaretForward } from 'react-icons/io5';
import { ValidatedInputString } from '../Form/ValidatedInputString';
import openapi_schema from '../../../../openapi_schema.json';
import { ValidatedInputDatetimeLocal } from '../Form/ValidatedInputDatetimeLocal';
import { Button1, Button2, ButtonSubmit } from '../Utils/Button';
import { Card1, CardButton } from '../Utils/Card';
import { Toggle1 } from '../Utils/Toggle';
import { config } from '../../config/config';
import { useValidatedInput } from '../../utils/useValidatedInput';
import { CheckOrX } from '../Form/CheckOrX';
import { IoCaretUp, IoCaretDown } from 'react-icons/io5';
import { useLocation, useNavigate } from 'react-router-dom';
import { Loader1 } from '../Utils/Loader';
import { Surface } from '../Utils/Surface';
import { Pagination } from '../Utils/Pagination';

type GetApiKeyJwtResponses = typeof getApiKeyJwt.responses;

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
  apiKeyCreate: Parameters<typeof postApiKey.call>[0]['data']
) => Promise<boolean>;
type TUpdateApiKeyFunc = (
  apiKeyId: Parameters<typeof patchApiKey.call>[0]['pathParams']['api_key_id'],
  apiKeyUpdate: Parameters<typeof patchApiKey.call>[0]['data']
) => Promise<boolean>;
type TDeleteApiKeyFunc = (index: number) => Promise<boolean>;

interface ApiKeyCodeModalProps {
  authContext: AuthContextType;
  apiKey: TApiKey;
}

function ApiKeyCodeModal({ apiKey, authContext }: ApiKeyCodeModalProps) {
  const [loading, setLoading] = useState<boolean>(true);
  const [jwt, setJwt] = useState<TJwt>(null);
  const [copySuccess, setCopySuccess] = useState<boolean>(false);

  async function fetchJwt(apiKeyId: TApiKey['id']) {
    setLoading(true);
    setCopySuccess(false);
    const { data, status } = await getApiKeyJwt.call({
      authContext,
      pathParams: {
        api_key_id: apiKeyId,
      },
    });
    if (status === 200) {
      const apiData = data as GetApiKeyJwtResponses['200'];
      setJwt(apiData.jwt);
    } else {
      return null;
    }
    setLoading(false);
  }

  useEffect(() => {
    setCopySuccess(false);
    fetchJwt(apiKey.id);
  }, [apiKey]);

  useEffect(() => {
    if (copySuccess) {
      const timeout = setTimeout(() => {
        setCopySuccess(false);
      }, 2000);
      return () => clearTimeout(timeout);
    }
  }, [copySuccess]);

  function copyCode() {
    navigator.clipboard.writeText(jwt).then(
      () => {
        setCopySuccess(true);
      },
      (err) => {
        console.error('Failed to copy text: ', err);
      }
    );
  }

  return (
    <div
      id="api-key-code"
      className="flex flex-col justify-between space-y-2 h-full"
    >
      <Card1
        onClick={() => copyCode()}
        className="hover:border-primary-light dark:hover:border-primary-dark cursor-pointer"
      >
        {loading ? (
          <Loader1 />
        ) : jwt ? (
          <code className="break-words">{jwt}</code>
        ) : (
          <p>Error generating code</p>
        )}
      </Card1>
      <div className="flex flex-col space-y-4">
        <p className="text-center h-4">
          {copySuccess ? 'Copied to clipboard' : null}
        </p>
        <Button1 onClick={() => copyCode()}>Copy Code</Button1>
      </div>
    </div>
  );
}

interface UpdateApiKeyProps {
  authContext: AuthContextType;
  apiKey: TApiKey;
  updateApiKeyFunc: TUpdateApiKeyFunc;
}

function UpdateApiKey({
  authContext,
  apiKey,
  updateApiKeyFunc,
}: UpdateApiKeyProps) {
  interface ValidatedApiKeyAvailable {
    name: ValidatedInputState<string>;
    expiry: ValidatedInputState<Date | null>;
  }

  const [loading, setLoading] = useState<boolean>(false);

  const [name, setName] = useState<ValidatedInputState<string>>({
    ...defaultValidatedInputState<string>(apiKey.name),
  });
  const [nameModified, setNameModified] = useState<boolean>(false);
  const [expiry, setExpiry] = useState<ValidatedInputState<Date | null>>({
    ...defaultValidatedInputState<Date | null>(new Date(apiKey.expiry)),
  });
  const [expiryModified, setExpiryModified] = useState<boolean>(false);
  const [modified, setModified] = useState<boolean>(false);

  const [updateApiKeyInputStatus, setUpdateApiKeyInputStatus] =
    useState<ValidatedInputState<any>['status']>(null);

  useEffect(() => {
    setNameModified(apiKey.name !== name.value);
  }, [name.value, apiKey]);

  useEffect(() => {
    setExpiryModified(
      expiry.value === null
        ? true
        : new Date(apiKey.expiry).getTime() !== new Date(expiry.value).getTime()
    );
  }, [expiry.value, apiKey]);

  useEffect(() => {
    setModified(nameModified || expiryModified);
  }, [nameModified, expiryModified]);

  useEffect(() => {
    setUpdateApiKeyInputStatus((prev) =>
      name.status === 'invalid' || expiry.status === 'invalid'
        ? 'invalid'
        : name.status === 'loading' || expiry.status === 'loading'
        ? 'loading'
        : 'valid'
    );
  }, [name, expiry]);

  return (
    <form
      id="update-api-key"
      onSubmit={async (e) => {
        e.preventDefault();
        setLoading(true);

        const apiKeyUpdate = {};
        if (nameModified) {
          apiKeyUpdate['name'] = name.value;
        }
        if (expiryModified) {
          apiKeyUpdate['expiry'] = new Date(expiry.value).toISOString();
        }
        if (await updateApiKeyFunc(apiKey.id, apiKeyUpdate)) {
        }
        setLoading(false);
      }}
      className="flex flex-col h-full"
    >
      <fieldset className="flex flex-col space-y-4">
        <section className="space-y-2">
          <label htmlFor="api-key-name">Name</label>
          <ValidatedInputString
            state={name}
            setState={setName}
            id="api-key-name"
            type="text"
            isAvailable={async (name) => {
              if (name === apiKey.name) {
                return true;
              } else {
                const { status } = await getIsApiKeyAvailable.call({
                  authContext,
                  params: {
                    name: name,
                  },
                });
                if (status === 200) {
                  return true;
                } else {
                  return false;
                }
              }
            }}
            checkAvailability={true}
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
        <section className="space-y-2">
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
      <div className="h-[4rem] flex flex-row justify-center space-x-2 items-center">
        {loading ? (
          <Loader1 />
        ) : modified ? (
          <>
            <CheckOrX status={updateApiKeyInputStatus} />
            <p className="text-center">
              {updateApiKeyInputStatus === 'valid'
                ? 'Available'
                : updateApiKeyInputStatus === 'loading'
                ? 'Checking'
                : updateApiKeyInputStatus === 'invalid'
                ? 'Not available'
                : 'error'}
            </p>
          </>
        ) : null}
      </div>
      <div className="flex flex-row space-x-4">
        <Button2
          className="flex-1"
          disabled={!modified}
          onClick={(e) => {
            e.preventDefault();
            setName({
              ...defaultValidatedInputState<string>(apiKey.name),
            });
            setExpiry({
              ...defaultValidatedInputState<Date>(new Date(apiKey.expiry)),
            });
          }}
        >
          Cancel
        </Button2>
        <Button1
          className="flex-1"
          disabled={updateApiKeyInputStatus !== 'valid' || !modified || loading}
          type="submit"
        >
          Submit
        </Button1>
      </div>
    </form>
  );
}

interface AddApiKeyProps {
  authContext: AuthContextType;
  addApiKeyFunc: TAddApiKeyFunc;
  modalsContext: ModalsContextType;
}

const addApiKeyModalKey = 'modal-add-api-key';

function AddApiKey({
  authContext,
  addApiKeyFunc,
  modalsContext,
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
    isAvailable: async (state) => {
      const { status } = await getIsApiKeyAvailable.call({
        authContext,
        params: {
          name: state.name.value,
        },
      });
      if (status === 200) {
        return true;
      } else {
        return false;
      }
    },
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
            modalsContext.deleteModals([addApiKeyModalKey]);
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
  scopeIds: Set<ScopeID>;
  deleteApiKeyScopeFunc: TModifyApiKeyScopeFunc;
  addApiKeyScopeFunc: TModifyApiKeyScopeFunc;
}

function ApiKeyTableRowScope({
  scopeId,
  apiKey,
  scopeIds,
  addApiKeyScopeFunc,
  deleteApiKeyScopeFunc,
}: ApiKeyTableRowScopeProps) {
  const debounceTimeout = useRef(null);
  const [debouncedState, setDebouncedState] = useState(scopeIds.has(scopeId));

  useEffect(() => {
    if (debounceTimeout.current) {
      clearTimeout(debounceTimeout.current);
    }

    if (scopeIds.has(scopeId) !== debouncedState) {
      debounceTimeout.current = setTimeout(async () => {
        if (debouncedState) {
          addApiKeyScopeFunc(apiKey, scopeId);
        } else {
          deleteApiKeyScopeFunc(apiKey, scopeId);
        }
      }, 500);
    }
  }, [debouncedState, scopeIds, scopeId]);

  return (
    <Toggle1
      onClick={async (e) => {
        e.stopPropagation();
        setDebouncedState((prev) => !prev);
      }}
      state={debouncedState}
    />
  );
}

const deleteApiKeyModalKey = 'modal-confirmation-delete-api-key';

interface ApiKeyViewProps {
  selectedIndex: number;
  setSelectedIndex: React.Dispatch<React.SetStateAction<number>>;
  apiKey: TApiKey;
  scopeIds: Set<ScopeID>;
  availableScopeIds: ScopeID[];
  updateApiKeyFunc: TUpdateApiKeyFunc;
  deleteApiKeyScopeFunc: TModifyApiKeyScopeFunc;
  addApiKeyScopeFunc: TModifyApiKeyScopeFunc;
  deleteApiKeyFunc: TDeleteApiKeyFunc;
  authContext: AuthContextType;
  modalsContext: ModalsContextType;
  activateButtonConfirmation: ReturnType<
    typeof useConfirmationModal
  >['activateButtonConfirmation'];
}

function makeApiKeyModalViewKey(id: TApiKey['id']): string {
  return `modal-api-key-view-${id}`;
}

function ApiKeyView({
  selectedIndex,
  setSelectedIndex,
  apiKey,
  scopeIds,
  availableScopeIds,
  updateApiKeyFunc,
  deleteApiKeyScopeFunc,
  addApiKeyScopeFunc,
  deleteApiKeyFunc,
  authContext,
  modalsContext,
  activateButtonConfirmation,
}: ApiKeyViewProps) {
  type Mode = 'code' | 'scopes' | 'edit';

  const modes: Mode[] = ['edit', 'scopes', 'code'];
  const [mode, setMode] = useState<Mode>(modes[0]);

  return (
    <div className="flex flex-col space-y-4 mt-2">
      <div className="flex flex-row justify-between items-center space-x-4">
        <div className="overflow-x-auto overflow-y-clip">
          <h3 className="break-words">{apiKey.name}</h3>
        </div>
      </div>
      <div className="flex flex-row space-x-2 overflow-x-auto">
        {modes.map((m) => (
          <Button2
            key={m}
            onClick={() => setMode(m)}
            className={`${
              mode === m ? ' border-primary-light dark:border-primary-dark' : ''
            } hover:border-primary-light dark:hover:border-primary-dark flex-1`}
          >
            {m}
          </Button2>
        ))}
        <Button2
          className="flex-1"
          onClick={() => {
            activateButtonConfirmation({
              key: deleteApiKeyModalKey,
              componentProps: {
                title: 'Delete API Key?',
                confirmText: 'Delete',
                message: `Are you sure you want to delete the API Key ${apiKey.name}?`,
                onConfirm: () => {
                  modalsContext.deleteModals([
                    makeApiKeyModalViewKey(apiKey.id),
                  ]);
                  deleteApiKeyFunc(selectedIndex);
                  setSelectedIndex(null);
                },
              },
            });
          }}
        >
          <span className="text-red-500">delete</span>
        </Button2>
      </div>
      <div className="flex flex-col min-h-[300px] h-full overflow-y-scroll">
        {mode === 'code' ? (
          <ApiKeyCodeModal apiKey={apiKey} authContext={authContext} />
        ) : mode === 'scopes' ? (
          <>
            {availableScopeIds.map((scopeId) => (
              <div
                className="flex flex-row items-center space-x-2"
                key={scopeId}
              >
                <ApiKeyTableRowScope
                  scopeId={scopeId}
                  apiKey={apiKey}
                  scopeIds={scopeIds}
                  addApiKeyScopeFunc={addApiKeyScopeFunc}
                  deleteApiKeyScopeFunc={deleteApiKeyScopeFunc}
                />
                <span>{config.scopeIdMapping[scopeId]}</span>
              </div>
            ))}
          </>
        ) : mode === 'edit' ? (
          <UpdateApiKey
            apiKey={apiKey}
            authContext={authContext}
            updateApiKeyFunc={updateApiKeyFunc}
          />
        ) : null}
      </div>
    </div>
  );
}

interface ApiKeysProps {
  authContext: AuthContextType;
  toastContext: ToastContextType;
}

export function ApiKeys({
  authContext,
  toastContext,
}: ApiKeysProps): JSX.Element {
  const modalsContext = useContext(ModalsContext);
  const { activateButtonConfirmation } = useConfirmationModal();

  type Params = Parameters<typeof getApiKeysSettingsPage.call>[0]['params'];
  type ParamKey = keyof Params;
  type OrderByArray = Params['order_by'];
  type OrderByField = GetElementTypeFromArray<OrderByArray>;

  const navigate = useNavigate();
  const query = new URLSearchParams(useLocation().search);

  const queryParameters =
    openapi_schema['paths']['/pages/settings/api-keys/']['get']['parameters'];

  const queryParamObjects: Record<ParamKey, any> = queryParameters.reduce(
    (acc, param) => {
      acc[param.name as ParamKey] = param;
      return acc;
    },
    {} as Record<ParamKey, any>
  );

  const orderByFields = new Set<OrderByField>(
    queryParamObjects['order_by'].schema.items.enum as OrderByArray
  );

  function getLimitFromQuery(limit: string): Params['limit'] {
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

  function getOffsetFromQuery(offset: string): Params['offset'] {
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

  function getOrderByFromQuery(orderBy: OrderByArray): OrderByArray {
    return orderBy.filter((field: OrderByField) => orderByFields.has(field));
  }

  const [limit, setLimit] = useState<Params['limit']>(
    getLimitFromQuery(query.get('limit'))
  );

  const [offset, setOffset] = useState<Params['offset']>(
    getOffsetFromQuery(query.get('offset'))
  );

  const [orderBy, setOrderBy] = useState<Params['order_by']>(
    getOrderByFromQuery(query.getAll('order_by') as OrderByArray)
  );

  const [orderByDesc, setOrderByDesc] = useState<Params['order_by_desc']>(
    getOrderByFromQuery(query.getAll('order_by_desc') as OrderByArray)
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

  const [apiKeyCount, setApiKeyCount] = useState<number>(null);
  const [apiKeys, setApiKeys] = useState<TApiKeys>({});
  const [apiKeyIdIndex, setApiKeyIdIndex] = useState<TApiKey['id'][]>([]);
  const [apiKeyScopeIds, setApiKeyScopeIds] = useState<TApiKeyScopeIds>({});
  const [availableScopeIds, setAvailableScopeIds] = useState<ScopeID[]>([]);

  const [selectedIndex, setSelectedIndex] = useState<number>(null);

  // show the available scopes based on the user's role
  useEffect(() => {
    if (authContext.state.user !== null) {
      setAvailableScopeIds(
        config.userRoleScopes[
          config.userRoleIdMapping[authContext.state.user.user_role_id]
        ].map((user_role_scope: string) => {
          return config.scopeNameMapping[user_role_scope];
        })
      );
    }
  }, [authContext]);

  const { data, status, loading, refetch } = useApiCall(
    getApiKeysSettingsPage,
    {
      authContext,
      params: {
        limit: limit,
        offset: offset,
        order_by: orderBy,
        order_by_desc: orderByDesc,
      },
    }
  );

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
        const apiData =
          data as (typeof getApiKeysSettingsPage.responses)['200'];
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

    const { data, status } = await postApiKeyScope.call({
      authContext,
      pathParams: {
        api_key_id: apiKey.id,
        scope_id: scopeId,
      },
    });
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
    const scopeName = config.scopeIdMapping[scopeId];

    setApiKeyScopeIds((prev) => {
      const updatedSet = new Set(prev[apiKey.id]);
      updatedSet.delete(scopeId);
      return {
        ...prev,
        [apiKey.id]: updatedSet,
      };
    });

    const { data, status } = await deleteApiKeyScope.call({
      authContext,
      pathParams: {
        api_key_id: apiKey.id,
        scope_id: scopeId,
      },
    });

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

    const { data, status } = await postApiKey.call({
      authContext,
      data: apiKeyCreate,
    });

    if (status === 200) {
      const apiData = data as (typeof postApiKey.responses)['200'];
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

    // optimistic update
    const apiKey = apiKeys[apiKeyId];
    setApiKeys((prev) => {
      const updated = { ...prev };
      updated[apiKeyId] = { ...updated[apiKeyId], ...apiKeyUpdate };
      return updated;
    });

    const { data, status } = await patchApiKey.call({
      authContext,
      pathParams: {
        api_key_id: apiKeyId,
      },
      data: apiKeyUpdate,
    });

    if (status === 200) {
      const apiData = data as (typeof postApiKey.responses)['200'];
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

      // revert optimistic update
      setApiKeys((prev) => {
        const updated = { ...prev };
        updated[apiKeyId] = { ...apiKey };
        return updated;
      });

      return false;
    }
  };

  const deleteApiKeyFunc: TDeleteApiKeyFunc = async (index) => {
    const apiKeyId = apiKeyIdIndex[index];
    const apiKey = apiKeys[apiKeyId];

    let toastId = toastContext.makePending({
      message: `Deleting API Key ${apiKey.name}`,
    });

    setApiKeyIdIndex((prev) => {
      const newApiKeyIdIndex = [...prev];
      newApiKeyIdIndex.splice(index, 1);
      return newApiKeyIdIndex;
    });
    setApiKeyCount((prev) => prev - 1);

    const { data, status } = await deleteApiKey.call({
      authContext,
      pathParams: {
        api_key_id: apiKeyId,
      },
    });

    if (status === 204) {
      const apiData = data as (typeof deleteApiKey.responses)['204'];
      toastContext.update(toastId, {
        message: `Deleted API Key ${apiKey.name}`,
        type: 'success',
      });

      setApiKeys((prev) => {
        const updated = { ...prev };
        delete updated[apiKeyId];
        return updated;
      });

      refetch();
      return true;
    } else {
      toastContext.update(toastId, {
        message: `Error deleting API Key ${apiKey.name}`,
        type: 'error',
      });

      setApiKeyIdIndex((prev) => {
        const updated = [...prev];
        updated.splice(index, 0, apiKeyId);
        return updated;
      });
      setApiKeyCount((prev) => prev + 1);

      return false;
    }
  };

  const selectedIndexRef = useRef(selectedIndex);
  const apiKeyViewFirstRenderRef = useRef(true);

  useEffect(() => {
    selectedIndexRef.current = selectedIndex;
  }, [selectedIndex]);

  useEffect(() => {
    if (selectedIndex !== null) {
      if (apiKeyViewFirstRenderRef.current) {
        const modal: ModalType<ApiKeyViewProps> = {
          key: makeApiKeyModalViewKey(apiKeyIdIndex[selectedIndex]),
          Component: ApiKeyView,
          componentProps: {
            selectedIndex: selectedIndex,
            setSelectedIndex: setSelectedIndex,
            apiKey: apiKeys[apiKeyIdIndex[selectedIndex]],
            scopeIds: apiKeyScopeIds[apiKeyIdIndex[selectedIndex]],
            availableScopeIds,
            updateApiKeyFunc,
            deleteApiKeyScopeFunc,
            deleteApiKeyFunc,
            addApiKeyScopeFunc,
            authContext,
            modalsContext,
            activateButtonConfirmation,
          },
          contentAdditionalClassName: 'max-w-[400px] w-full',
          onExit: () => setSelectedIndex(null),
        };
        modalsContext.pushModals([modal]);
        apiKeyViewFirstRenderRef.current = false;
      }
    } else {
      apiKeyViewFirstRenderRef.current = true;
    }
  }, [selectedIndex]);

  useEffect(() => {
    if (
      selectedIndexRef.current !== null &&
      !apiKeyViewFirstRenderRef.current
    ) {
      const modal: ModalUpdateType<ApiKeyViewProps> = {
        key: makeApiKeyModalViewKey(apiKeyIdIndex[selectedIndex]),
        componentProps: {
          apiKey: apiKeys[apiKeyIdIndex[selectedIndex]],
          scopeIds: apiKeyScopeIds[apiKeyIdIndex[selectedIndex]],
          availableScopeIds,
        },
      };
      modalsContext.updateModals([modal]);
    }
  }, [apiKeys, apiKeyScopeIds, availableScopeIds]);

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
                  modalsContext.pushModals([
                    {
                      key: addApiKeyModalKey,
                      Component: AddApiKey,
                      componentProps: {
                        authContext,
                        addApiKeyFunc,
                        modalsContext,
                      },
                      contentAdditionalClassName: 'max-w-[350px] w-full',
                    },
                  ]);
                }}
              >
                Add API Key
              </Button1>
            </div>
            <Pagination
              loading={loading}
              offset={offset}
              setOffset={setOffset}
              limit={limit}
              setLimit={setLimit}
              count={apiKeyIdIndex.length}
              total={apiKeyCount}
            />
          </div>

          <div className="overflow-x-auto mt-4">
            <table className="min-w-full">
              <thead className="text-left">
                <tr>
                  {['name', 'issued', 'expiry'].map((field: OrderByField) => (
                    <th key={field}>
                      {(() => {
                        let orderByState: OrderByState = 'off';

                        // get index of field in orderBy
                        const orderByIndex = orderBy.indexOf(field);
                        if (orderByIndex !== -1) {
                          orderByState = 'asc';
                        }
                        const orderByDescIndex = orderByDesc.indexOf(field);
                        if (orderByDescIndex !== -1) {
                          orderByState = 'desc';
                        }

                        return (
                          <>
                            {orderByFields.has(field) ? (
                              <div
                                className="flex flex-row items-center surface-hover cursor-pointer pl-2"
                                onClick={() => {
                                  if (orderByState === 'off') {
                                    setOrderBy((prev) => {
                                      const updated = [...prev, field];
                                      return updated;
                                    });
                                  } else if (orderByState === 'asc') {
                                    setOrderByDesc((prev) => {
                                      const updated = [...prev, field];
                                      return updated;
                                    });
                                  } else if (orderByState === 'desc') {
                                    setOrderBy((prev) => {
                                      const updated = prev.filter(
                                        (item) => item !== field
                                      );
                                      return updated;
                                    });
                                    setOrderByDesc((prev) => {
                                      const updated = prev.filter(
                                        (item) => item !== field
                                      );
                                      return updated;
                                    });
                                  }
                                }}
                              >
                                {field}
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
                                      const index = orderBy.indexOf(field);
                                      return index + 1;
                                    })()}
                                  </>
                                )}
                              </div>
                            ) : (
                              field
                            )}
                          </>
                        );
                      })()}
                    </th>
                  ))}
                  {availableScopeIds.map((scopeId) => (
                    <th key={scopeId}>{config.scopeIdMapping[scopeId]}</th>
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
                      <td className="px-2 py-1 truncate">
                        {apiKeys[apiKeyId].name}
                      </td>
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
                            scopeIds={apiKeyScopeIds[apiKeyId]}
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
