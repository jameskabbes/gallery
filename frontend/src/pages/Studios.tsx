import React, { useState, useEffect } from 'react';
import { callApi, useApiData } from '../utils/Api';
import { paths, operations, components } from '../openapi_schema';
import { ApiResponse, ExtractResponseTypes } from '../types';
import { Link as StudioLink } from '../components/Studio/Link';
import { CreateStudio } from '../components/Studio/CreateStudio';

const API_PATH = '/pages/studios/';
const API_METHOD = 'get';

type AllResponseTypes = ExtractResponseTypes<
  paths[typeof API_PATH][typeof API_METHOD]['responses']
>;

function Studios(): JSX.Element {
  const { apiData, loading, status } = useApiData(API_PATH);
  const [creatingStudio, setCreatingStudio] = useState(false);

  if (loading || status == 200) {
    const data = apiData as AllResponseTypes['200'];
    return (
      <div>
        {data === null ? (
          <p>loading...</p>
        ) : (
          <ul>
            {data.studios.map((studio) => (
              <li key={studio.id}>
                <StudioLink studio_id={studio.id}>{studio.name}</StudioLink>
              </li>
            ))}
          </ul>
        )}
        {creatingStudio ? (
          <CreateStudio />
        ) : (
          <button onClick={() => setCreatingStudio(true)}>Create Studio</button>
        )}
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
