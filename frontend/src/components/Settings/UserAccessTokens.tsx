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

const API_ENDPOINT = '/user-access-tokens/';
const API_METHOD = 'get';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

interface Props {
  authContext: AuthContextType;
  toastContext: ToastContextType;
}

function UserAccessTokens({ authContext, toastContext }: Props): JSX.Element {
  const [userAccessTokens, setUserAccessTokens] = useState<{
    [key: string]: ResponseTypesByStatus['200'][number];
  }>({});

  const {
    data: apiData,
    loading,
    status,
  } = useApiCall<ResponseTypesByStatus[keyof ResponseTypesByStatus]>({
    url: API_ENDPOINT,
    method: API_METHOD,
  });

  useEffect(() => {
    if (apiData && status === 200) {
      const userAccessTokensObject = (
        apiData as ResponseTypesByStatus['200']
      ).reduce((acc, session) => {
        acc[session.id] = session;
        return acc;
      }, {} as { [key: string]: ResponseTypesByStatus['200'][number] });
      setUserAccessTokens(userAccessTokensObject);
    }
  }, [apiData, status]);

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

    const { data, status } = await deleteUserAccessToken(
      authContext,
      sessionId
    );

    if (status === 204) {
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
        <>
          <h2 className="mb-4">Sessions</h2>
          <div className="flex flex-col space-y-4">
            {Object.keys(userAccessTokens).map((key) => {
              const session = userAccessTokens[key];
              return (
                <Card1
                  key={key}
                  className="flex flex-row justify-between items-center"
                >
                  <p>
                    Issued:{' '}
                    {new Date(session.issued).toLocaleString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                      hour: 'numeric',
                      minute: 'numeric',
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
        </>
      )}
    </>
  );
}

export { UserAccessTokens };
