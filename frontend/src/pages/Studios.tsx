import React, { useState, useEffect } from 'react';
import { callApi, useApiData } from '../utils/Api';
import { paths, operations, components } from '../openapi_schema';

const API_PATH = '/studios/';

function Studios(): JSX.Element {
  const [data, setData, loading, setLoading, status, setStatus] =
    useApiData<
      paths[typeof API_PATH]['get']['responses']['200']['content']['application/json']
    >(API_PATH);

  useEffect(() => {
    console.log('data changed');
    console.log(data);
  }, [data]);

  async function deleteStudioId(studioId: components['schemas']['StudioId']) {
    // remove studioId from data.studios and data.studio_ids_to_delete

    const studioToBeDeleted = data.studios[studioId];

    setData((prev) => {
      if (!prev) {
        return prev;
      }

      let newStudios = { ...prev.studios };
      delete newStudios[studioId];
      let newStudioIdsToDelete = { ...prev.studio_ids_to_delete };
      delete newStudioIdsToDelete[studioId];

      return {
        ...prev,
        studios: newStudios,
        studio_ids_to_delete: newStudioIdsToDelete,
      };
    });

    setLoading(true);
    const response = await callApi<
      paths['/studios/{studio_id}']['delete']['responses']['200']['content']['application/json']
    >(`/studios/${studioId}`, 'DELETE');
    if (response.status !== 200 && response.status !== 204) {
      console.error(`Error deleting studio: ${response.status}`);
      setData((prev) => {
        if (!prev) {
          return prev;
        }
        let newStudios = { ...prev.studios };
        newStudios[studioId] = studioToBeDeleted;
        let newStudioIdsToDelete = { ...prev.studio_ids_to_delete };
        newStudioIdsToDelete[studioId] = null;
        return {
          ...prev,
          studios: newStudios,
          studio_ids_to_delete: newStudioIdsToDelete,
        };
      });
    }
    setLoading(false);
  }
  async function importStudio(studio: components['schemas']['Studio']) {
    //add studio to data.studios
    //remove studio from data.stusions_to_add

    setData((prev) => {
      if (!prev) {
        return prev;
      }

      let newStudios = { ...prev.studios };
      newStudios[studio._id] = studio;
      let newStudiosToAdd = { ...prev.studios_to_add };
      delete newStudiosToAdd[studio._id];

      return {
        ...prev,
        studios: newStudios,
        studios_to_add: newStudiosToAdd,
      };
    });

    setLoading(true);
    const response = await callApi<
      paths['/studios/']['post']['responses']['200']['content']['application/json']
    >(`/studios/`, 'POST', studio);
    console.log(response);

    if (response.status !== 200 && response.status !== 204) {
      console.error(`Error importing studio: ${response.status}`);
      // remove studio from studios
      setData((prev) => {
        if (!prev) {
          return prev;
        }
        const newStudios = { ...prev.studios };
        delete newStudios[studio._id];
        return {
          ...prev,
          studios: newStudios,
        };
      });
    }
    setLoading(false);
  }

  return (
    <div>
      <h1>Studios</h1>
      {data && (
        <div>
          <ul>
            {Object.keys(data.studios).map((studioId) => (
              <li key={studioId}>
                <div className="card">
                  {data.studios[studioId].dir_name}
                  {studioId in data.studio_ids_to_delete && (
                    <button onClick={() => deleteStudioId(studioId)}>
                      Delete
                    </button>
                  )}
                </div>
              </li>
            ))}
          </ul>
          {Object.keys(data.studios_to_add).length !== 0 && (
            <>
              <h2>Studios to Add</h2>
              <ul>
                {Object.keys(data.studios_to_add).map((studioId) => (
                  <li key={data.studios_to_add[studioId]._id}>
                    <div className="card">
                      {data.studios_to_add[studioId].dir_name}
                      <button
                        onClick={() =>
                          importStudio(data.studios_to_add[studioId])
                        }
                      >
                        Import
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
