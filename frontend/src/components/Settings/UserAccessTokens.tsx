import React, { useEffect, useState } from 'react';
import {
  CallApiProps,
  ToastContext,
  ExtractResponseTypes,
  AuthContext,
} from '../../types';
import { useApiCall } from '../../utils/Api';
import { paths, operations, components } from '../../openapi_schema';
import {
  deleteUserAccessToken,
  ResponseTypesByStatus as DeleteUserAccessTokenResponseTypes,
} from '../../services/api/deleteUserAccessToken';
import { Card1 } from '../Utils/Card';
import { Button1 } from '../Utils/Button';

const API_ENDPOINT = '/user-access-tokens/';
const API_METHOD = 'get';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

interface Props {
  authContext: AuthContext;
  toastContext: ToastContext;
}

function UserAccessTokens({ authContext, toastContext }: Props): JSX.Element {
  const [userAccessTokens, setUserAccessTokens] = useState<{
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
      const userAccessTokensObject = (
        apiData as ResponseTypesByStatus['200']
      ).reduce((acc, session) => {
        acc[session.id] = session;
        return acc;
      }, {} as { [key: string]: ResponseTypesByStatus['200'][number] });
      setUserAccessTokens(userAccessTokensObject);
    }
  }, [apiData, response]);

  async function handleDeleteSession(
    sessionId: components['schemas']['UserAccessToken']['id']
  ) {
    let toastId = toastContext.makePending({
      message: 'Deleting session...',
    });

    const sessionToDelete = userAccessTokens[sessionId];

    setUserAccessTokens((prevUserAccessTokens) => {
      const newUserAccessTokens = { ...prevUserAccessTokens };
      delete newUserAccessTokens[sessionId];
      return newUserAccessTokens;
    });

    const { data, response } = await deleteUserAccessToken(sessionId);

    if (response.status === 204) {
      const apiData = data as DeleteUserAccessTokenResponseTypes['204'];
      toastContext.update(toastId, {
        message: `Deleted session`,
        type: 'success',
      });
    } else {
      toastContext.update(toastId, {
        message: 'Could not delete session',
        type: 'error',
      });
      setUserAccessTokens((prevUserAccessTokens) => ({
        ...prevUserAccessTokens,
        [sessionId]: sessionToDelete,
      }));
    }
  }

  return (
    <>
      {authContext.state.user === null ? (
        <p>Login to view your sessions.</p>
      ) : (
        <div>
          {Object.keys(userAccessTokens).map((key) => {
            const session = userAccessTokens[key];
            return (
              <Card1
                key={key}
                className="flex flex-row justify-between items-center button-tertiary m-2"
              >
                <p>
                  Issued:{' '}
                  {new Date(session.issued).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                  })}
                </p>
                <Button1
                  onClick={() => {
                    handleDeleteSession(key);
                  }}
                >
                  Sign Out
                </Button1>
              </Card1>
            );
          })}
        </div>
      )}
    </>
  );
}

export { UserAccessTokens };
