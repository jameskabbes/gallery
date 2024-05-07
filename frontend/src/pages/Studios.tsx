import React, { useState, useEffect } from 'react';
import { callApi, useApiData } from '../utils/Api';
import { paths, operations, components } from '../openapi_schema';

const API_PATH = '/studios/';

function Studios(): JSX.Element {
  const [data, setData, loading, setLoading, status, setStatus] =
    useApiData<
      paths[typeof API_PATH]['get']['responses']['200']['content']['application/json']
    >(API_PATH);

  // set of whatever the ids_to_delete are
  const [idsToDeleteSet, setIdsToDeleteSet] = useState<
    Set<components['schemas']['StudioId']>
  >(new Set());

  // useEffect whenever data.studios.ids_to_delete changes, convert it to a set
  useEffect(() => {
    if (data) {
      setIdsToDeleteSet(new Set(data.ids_to_delete));
    }
  }, [data]);

  console.log(data);

  async function deleteStudio(studioId: components['schemas']['StudioId']) {
    setLoading(true);
    const response = await callApi<
      paths[typeof API_PATH]['get']['responses']['200']['content']['application/json']
    >(`/studios/${studioId}/delete/`, 'POST');
    if (response.status === 200) {
      setData(response.data);
      setStatus(response.status);
    } else {
      console.error(`Error deleting studio: ${response.status}`);
    }
    setLoading(false);
  }
  async function importStudio(
    dirName: components['schemas']['Studio']['dir_name']
  ) {
    setLoading(true);
    const response = await callApi<
      paths[typeof API_PATH]['get']['responses']['200']['content']['application/json']
    >(`/studios/${dirName}/import/`, 'POST');
    if (response.status === 200) {
      setData(response.data);
      setStatus(response.status);
    } else {
      console.error(`Error importing studio: ${response.status}`);
    }
    setLoading(false);
  }

  return (
    <div>
      <h1>Studios</h1>
      {data && (
        <div>
          <ul>
            {Object.keys(data.studios).map((key) => (
              <li key={key}>
                <div className="card">{data.studios[key].dir_name}</div>
              </li>
            ))}
          </ul>
          {data.dir_names_to_add.length !== 0 && (
            <>
              <h2>Studios to Add</h2>
              <ul>
                {data.dir_names_to_add.map((dirName) => (
                  <li key={dirName}>
                    <div className="card">
                      {dirName}
                      <button onClick={() => importStudio(dirName)}>
                        Import
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            </>
          )}
          {data.ids_to_delete.length !== 0 && (
            <>
              <h2>Studios to Delete</h2>
              <ul>
                {data.ids_to_delete.map((studioId) => (
                  <li key={studioId}>
                    <div className="card">
                      <span>{data.studios[studioId].dir_name}</span>
                      <button onClick={() => deleteStudio(studioId)}>
                        Delete
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}
    </div>
  );
}

export { Studios };
