import React, { useEffect, useState } from 'react';
import {
  CallApiProps,
  ToastContext,
  ExtractResponseTypes,
  AuthContext,
} from '../../types';
import { useApiCall } from '../../utils/Api';
import { paths, operations, components } from '../../openapi_schema';
import { deleteAuthCredential } from '../../services/api/deleteAuthCredential';

const API_ENDPOINT = '/sessions/';
const API_METHOD = 'get';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

interface Props {
  authContext: AuthContext;
  toastContext: ToastContext;
}

function Sessions({ authContext, toastContext }: Props): JSX.Element {
  const [sessions, setSessions] = useState<{
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
      const sessionsObject = (apiData as ResponseTypesByStatus['200']).reduce(
        (acc, session) => {
          acc[session.id] = session;
          return acc;
        },
        {} as { [key: string]: ResponseTypesByStatus['200'][number] }
      );
      setSessions(sessionsObject);
    }
  }, [apiData, response]);

  async function handleDeleteSession(sessionId: string) {
    console.log(sessions);

    const sessionToDelete = sessions[sessionId];

    const newSessions = { ...sessions };
    delete newSessions[sessionId];
    setSessions(newSessions);

    const { data, response } = await deleteAuthCredential(
      sessionId,
      toastContext
    );

    console.log(data);
    console.log(response);

    if (response.status !== 204) {
      setSessions({ ...sessions, [sessionId]: sessionToDelete });
    }
  }

  return (
    <>
      <h2>Sessions</h2>
      {authContext.state.user === null ? (
        <p>Login to view your sessions.</p>
      ) : (
        <div>
          {Object.keys(sessions).map((key) => {
            const session = sessions[key];
            return (
              <div key={key} className="flex flex-row">
                <p>
                  Issued:{' '}
                  {new Date(session.issued).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                  })}
                </p>
                <button
                  onClick={() => {
                    handleDeleteSession(key);
                  }}
                  className="button-primary"
                >
                  Sign Out
                </button>
              </div>
            );
          })}
        </div>
      )}
    </>
  );
}

export { Sessions };
