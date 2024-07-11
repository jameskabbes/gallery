import React, { useState, useEffect } from 'react';
import { callApi, useApiData } from '../utils/Api';
import { paths, operations, components } from '../openapi_schema';
import { Link } from 'react-router-dom';

const API_PATH = '/pages/studios/';

function Studios(): JSX.Element {
  const [data, setData, loading, setLoading, status, setStatus] =
    useApiData<
      paths[typeof API_PATH]['get']['responses']['200']['content']['application/json']
    >(API_PATH);

  function deleteStudio(id: components['schemas']['StudioID']) {
    callApi<paths['/studios/{studio_id}/']['delete']['responses']>(
      `/studios/${id}/`
    );
  }

  return (
    <div>
      <h1>Studios</h1>
      <ul>
        {data !== null &&
          data.studios.map((studio) => (
            <li key={studio.id}>
              <div className="flex flex-row items-center">
                <p>{studio.name}</p>
                <button onClick={}>Delete</button>
              </div>
            </li>
          ))}
      </ul>
      <button>Add Studio</button>
    </div>
  );
}

export { Studios };
