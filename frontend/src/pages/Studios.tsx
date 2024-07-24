import React, { useState, useEffect, useContext } from 'react';
import { callApi, useApiData } from '../utils/Api';
import { paths, operations, components } from '../openapi_schema';
import { ApiResponse, ExtractResponseTypes } from '../types';
import { Link as StudioLink } from '../components/Studio/Link';
import { CreateStudio } from '../components/Studio/CreateStudio';
import { DataContext } from '../contexts/Data';
import { ConfirmationModalContext } from '../contexts/ConfirmationModal';
import { deleteStudioFunc } from '../components/Studio/deleteStudioFunc';

const API_PATH = '/pages/studios/';
const API_METHOD = 'get';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_PATH][typeof API_METHOD]['responses']
>;

function Studios(): JSX.Element {
  const { apiData, loading, status } =
    useApiData<ResponseTypesByStatus[keyof ResponseTypesByStatus]>(API_PATH);
  const Data = useContext(DataContext);
  const ConfirmationModal = useContext(ConfirmationModalContext);

  // update the studios in the DataContext with the API result
  useEffect(() => {
    if (status === 200) {
      const data = apiData as ResponseTypesByStatus['200'];
      if (data !== null) {
        let newStudios = new Map();
        data.studios.forEach((studio) => {
          newStudios.set(studio.id, studio);
        });
        Data.studios.dispatch({ type: 'SET', payload: newStudios });
      }
    }
  }, [status, apiData]);

  if (loading || status == 200) {
    const data = apiData as ResponseTypesByStatus['200'];
    return (
      <div>
        {Data.studios === null ? (
          <p>loading...</p>
        ) : (
          <ul>
            <p>Studios</p>
            {/* Help me sort things by name first  */}
            {Array.from(Data.studios.state.keys())
              .map((studioId) => Data.studios.state.get(studioId)) // Convert keys to studio objects
              .sort((a, b) => a.name.localeCompare(b.name)) // Sort studios by name
              .map((studio) => (
                <li key={studio.id}>
                  <div className="card flex flex-row justify-between">
                    {studio.name}
                    <StudioLink studio_id={studio.id}>
                      <p>Link</p>
                    </StudioLink>

                    <button
                      onClick={() => {
                        deleteStudioFunc(
                          studio,
                          Data.studios.dispatch,
                          ConfirmationModal.showModal
                        );
                      }}
                    >
                      Delete
                    </button>
                  </div>
                </li>
              ))}
          </ul>
        )}
        <CreateStudio />
      </div>
    );
  } else {
    return (
      <div>
        <h1>Error {status}</h1>
      </div>
    );
  }
}

export { Studios };
