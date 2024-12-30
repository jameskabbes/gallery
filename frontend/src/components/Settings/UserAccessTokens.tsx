import React, { useEffect, useState } from 'react';
import {
  ExtractResponseTypes,
  AuthContextType,
  ToastContextType,
} from '../../types';
import { useApiCall } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import {
  deleteUserAccessToken,
  DeleteUserAccessTokenResponses,
} from '../../services/api/deleteUserAccessToken';
import { Card1 } from '../Utils/Card';
import { Button1 } from '../Utils/Button';
import { useConfirmationModal } from '../../utils/useConfirmationModal';
import { Loader1 } from '../Utils/Loader';
import { useLocation, useNavigate } from 'react-router-dom';
import openapi_schema from '../../../../openapi_schema.json';
import { Pagination } from '../Utils/Pagination';

const API_ENDPOINT = '/pages/settings/user-access-tokens/';
const API_METHOD = 'get';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

type QueryParams =
  paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['query'];

interface Props {
  authContext: AuthContextType;
  toastContext: ToastContextType;
}

type TUserAccessToken = components['schemas']['UserAccessToken'];
type TUserAccessTokens = Record<TUserAccessToken['id'], TUserAccessToken>;

function UserAccessTokens({ authContext, toastContext }: Props): JSX.Element {
  const { activateButtonConfirmation } = useConfirmationModal();

  const navigate = useNavigate();
  const query = new URLSearchParams(useLocation().search);

  type QueryParamKey =
    keyof paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['query'];
  const queryParameters =
    openapi_schema['paths'][API_ENDPOINT][API_METHOD]['parameters'];

  const queryParamObjects: Record<QueryParamKey, any> = queryParameters.reduce(
    (acc, queryParam) => {
      acc[queryParam.name] = queryParam;
      return acc;
    },
    {} as Record<QueryParamKey, any>
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

  const [limit, setLimit] = useState<QueryParams['limit']>(
    getLimitFromQuery(query.get('limit'))
  );

  const [offset, setOffset] = useState<QueryParams['offset']>(
    getOffsetFromQuery(query.get('offset'))
  );

  //   Update URL when state changes
  useEffect(() => {
    const params = new URLSearchParams();
    if (limit !== queryParamObjects['limit'].schema.default)
      params.set('limit', limit.toString());
    if (offset !== queryParamObjects['offset'].schema.default)
      params.set('offset', offset.toString());

    const newSearch = params.toString();
    if (newSearch !== location.search) {
      navigate({ search: newSearch });
    }
  }, [limit, offset]);

  const [userAccessTokenCount, setUserAccessTokenCount] =
    useState<number>(null);
  const [userAccessTokens, setUserAccessTokens] = useState<TUserAccessTokens>(
    {}
  );
  const [userAccessTokenIdIndex, setUserAccessTokenIdIndex] = useState<
    TUserAccessToken['id'][]
  >([]);

  const { data, loading, status, refetch } = useApiCall<
    ResponseTypesByStatus[keyof ResponseTypesByStatus]
  >({
    url: API_ENDPOINT,
    method: API_METHOD,
    params: {
      limit: limit,
      offset: offset,
    },
  });

  const hasMounted = React.useRef(false);

  // refetch when limit, offset, orderBy, or orderByDesc changes
  useEffect(() => {
    if (hasMounted.current) {
      refetch();
    } else {
      hasMounted.current = true;
    }
  }, [offset, limit]);

  useEffect(() => {
    if (!loading) {
      if (status === 200) {
        const apiData = data as ResponseTypesByStatus['200'];

        setUserAccessTokenCount(apiData.user_access_token_count);
        setUserAccessTokens(() => {
          const newUserAccessTokens: TUserAccessTokens = {};
          for (const userAccessToken of apiData.user_access_tokens) {
            newUserAccessTokens[userAccessToken.id] = userAccessToken;
          }
          return newUserAccessTokens;
        });
        setUserAccessTokenIdIndex(() =>
          apiData.user_access_tokens.map(
            (userAccessToken) => userAccessToken.id
          )
        );
      }
    }
  }, [data, loading, status]);

  async function handleDeleteUserAccessToken(index: number) {
    const sessionId = userAccessTokenIdIndex[index];

    let toastId = toastContext.makePending({
      message: 'Deleting session...',
    });

    setUserAccessTokenIdIndex((prevUserAccessTokenIdIndex) => {
      const newUserAccessTokenIdIndex = [...prevUserAccessTokenIdIndex];
      newUserAccessTokenIdIndex.splice(index, 1);
      return newUserAccessTokenIdIndex;
    });

    const { data, status } = await deleteUserAccessToken(
      authContext,
      sessionId
    );

    if (status === 204) {
      toastContext.update(toastId, {
        message: `Deleted session`,
        type: 'success',
      });

      setUserAccessTokens((prevUserAccessTokens) => {
        const newUserAccessTokens = { ...prevUserAccessTokens };
        delete newUserAccessTokens[sessionId];
        return newUserAccessTokens;
      });

      if (
        authContext.state.auth_credential?.id === sessionId &&
        authContext.state.auth_credential?.type === 'access_token'
      ) {
        authContext.logOut();
      }
    } else {
      toastContext.update(toastId, {
        message: 'Could not delete session',
        type: 'error',
      });

      setUserAccessTokenIdIndex((prevUserAccessTokenIdIndex) => {
        // add the item back into the array at postiion index
        const newUserAccessTokenIdIndex = [...prevUserAccessTokenIdIndex];
        newUserAccessTokenIdIndex.splice(index, 0, sessionId);
        return newUserAccessTokenIdIndex;
      });
    }
  }

  if (authContext.state.user !== null) {
    return (
      <>
        <h2 className="mb-4">Sessions</h2>
        <Card1>
          <div className="flex flex-row justify-end">
            <Pagination
              loading={loading}
              offset={offset}
              setOffset={setOffset}
              limit={limit}
              setLimit={setLimit}
              count={userAccessTokenIdIndex.length}
              total={userAccessTokenCount}
            />
          </div>
          {userAccessTokenIdIndex.map((userAccessTokenId, index) => {
            const userAccessToken = userAccessTokens[userAccessTokenId];
            return (
              <Card1
                key={userAccessTokenId}
                className="flex flex-row justify-between items-center"
              >
                <p>
                  Issued:{' '}
                  {new Date(userAccessToken.issued).toLocaleString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: 'numeric',
                    minute: 'numeric',
                  })}
                </p>
                <p>
                  {authContext.state.auth_credential?.id ===
                    userAccessToken.id && <span>Current Session</span>}
                </p>
                <Button1
                  onClick={() => {
                    if (
                      authContext.state.auth_credential?.id ===
                      userAccessToken.id
                    ) {
                      activateButtonConfirmation({
                        componentProps: {
                          title: 'Sign Out?',
                          message:
                            'This will sign you out of your current session.',
                          onConfirm: () => handleDeleteUserAccessToken(index),
                          confirmText: 'Sign Out',
                        },
                      });
                    } else {
                      handleDeleteUserAccessToken(index);
                    }
                  }}
                >
                  Sign Out
                </Button1>
              </Card1>
            );
          })}
        </Card1>
      </>
    );
  }
}

export { UserAccessTokens };
