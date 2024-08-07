import React, { useState, useEffect, useContext } from 'react';
import { paths, operations, components } from '../openapi_schema';
import { StudioLink } from '../components/Studio/Link';
import { CreateStudio } from '../components/Studio/CreateStudio';
import { DataContext } from '../contexts/Data';
import { ConfirmationModalContext } from '../contexts/ConfirmationModal';
import { StudioCard } from '../components/Studio/Card';

import { ExtractResponseTypes } from '../types';
import { useBackendApiCall } from '../utils/Api';
import { deleteStudioFunc } from '../components/Studio/deleteStudioFunc';

const API_PATH = '/pages/studios/';
const API_METHOD = 'get';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_PATH][typeof API_METHOD]['responses']
>;

function Studios(): JSX.Element {
  const {
    data: apiData,
    loading,
    response,
  } = useBackendApiCall<ResponseTypesByStatus[keyof ResponseTypesByStatus]>({
    endpoint: API_PATH,
    method: API_METHOD,
  });

  const Data = useContext(DataContext);
  const ConfirmationModal = useContext(ConfirmationModalContext);

  // update the studios in the DataContext with the API result
  useEffect(() => {
    if (!loading) {
      if (response.status === 200) {
        const data = apiData as ResponseTypesByStatus['200'];
        if (data !== null) {
          let newStudios = new Map();
          data.studios.forEach((studio) => {
            newStudios.set(studio.id, studio);
          });
          Data.studios.dispatch({ type: 'SET', payload: newStudios });
        }
      }
    }
  }, [loading]);

  if (loading || response.status == 200) {
    const data = apiData as ResponseTypesByStatus['200'];
    return (
      <div>
        <h1>Studios</h1>
        {Data.studios === null ? (
          <p>loading...</p>
        ) : (
          <ul>
            {/* Help me sort things by name first  */}
            {Array.from(Data.studios.state.keys())
              .map((studioId) => Data.studios.state.get(studioId)) // Convert keys to studio objects
              .sort((a, b) => a.name.localeCompare(b.name)) // Sort studios by name
              .map((studio) => (
                <li key={studio.id}>
                  <StudioLink studio_id={studio.id}>
                    <StudioCard studio={studio} />
                  </StudioLink>
                  <button
                    onClick={() =>
                      deleteStudioFunc(
                        studio,
                        Data.studios.dispatch,
                        ConfirmationModal.showModal
                      )
                    }
                  >
                    Delete
                  </button>
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
        <h1>Error {response.status}</h1>
      </div>
    );
  }
}

export { Studios };
