import React, { useEffect, useState } from 'react';
import { CallApiProps, ToastContext } from '../../types';
import { useApiCall } from '../../utils/Api';
import { paths, operations, components } from '../../openapi_schema';
import { ExtractResponseTypes, AuthContext } from '../../types';
import { deleteAuthCredential } from '../../services/api/deleteAuthCredential';

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
    // delete the key from the object

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
      console.log('removign');
      //   setSessions({ ...sessions, [sessionId]: sessionToDelete });
    }
  }

  if (authContext.state.user === null) {
    return (
      <div>
        <h2>Sessions</h2>
        <p>Login to view your sessions.</p>
      </div>
    );
  } else if (loading || response.status == 200) {
    const data = apiData as ResponseTypesByStatus['200'];
    if (!data) {
      return <p>loading...</p>;
    }
    return (
      <div>
        {data.map((session) => (
          <div key={session.id} className="flex flex-row">
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
                handleDeleteSession(session.id);
              }}
              className="button-primary"
            >
              Sign Out
            </button>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div>
      <h2>Sessions</h2>
      <p>Manage your sessions here.</p>
    </div>
  );
}

export { APIKeys };
