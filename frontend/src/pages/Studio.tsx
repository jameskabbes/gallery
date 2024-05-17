import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { callApi, useApiData } from '../utils/Api';
import { paths, operations, components } from '../openapi_schema';

const API_PATH = '/studios/{studio_id}/page';

function Studio(): JSX.Element {
  const { studioId } = useParams();

  const [data, setData, loading, setLoading, status, setStatus] = useApiData<
    paths[typeof API_PATH]['get']['responses']['200']['content']['application/json']
  >(API_PATH.replace('{studio_id}', studioId));

  console.log(studioId);

  if (status == 404) {
    return <h1>Studio does not exist</h1>;
  }

  return (
    <>
      <h1>{data === null ? 'Studio' : data.studio.dir_name}</h1>
      <h2>Events</h2>
      <ul>
        {data === null ? (
          <p>loading events...</p>
        ) : (
          <>
            {Object.keys(data.events).map((eventId) => (
              <div className="card" key={eventId}>
                <li>
                  {data.events[eventId].datetime}
                  {data.events[eventId].name}
                  {eventId in data.event_ids_to_delete && (
                    <button onClick={() => {}}>Delete</button>
                  )}
                </li>
              </div>
            ))}
          </>
        )}
      </ul>
      {data !== null && Object.keys(data.events_to_add).length !== 0 && (
        <>
          <h2>Events to Add</h2>
          <ul>
            {Object.keys(data.events_to_add).map((eventId) => (
              <li key={data.events_to_add[eventId]._id}>
                <div className="card">
                  {data.events_to_add[eventId]?.name}
                  {data.events_to_add[eventId]?.datetime}
                  <button onClick={() => {}}>Import</button>
                </div>
              </li>
            ))}
          </ul>
        </>
      )}
    </>
  );
}

export { Studio };
