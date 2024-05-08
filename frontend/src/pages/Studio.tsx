import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { callApi, useApiData } from '../utils/Api';
import { paths, operations, components } from '../openapi_schema';

const API_PATH = '/studio/{studio_id}/';

function Studio(): JSX.Element {
  const { studioId } = useParams();

  const [data, setData, loading, setLoading, status, setStatus] = useApiData<
    paths[typeof API_PATH]['get']['responses']['200']['content']['application/json']
  >(API_PATH.replace('{studio_id}', studioId));

  console.log(data);

  return (
    <>
      {data && (
        <>
          <h1>
            {data.studio.dir_name} {data.studio.name}
          </h1>
          <h2>Events</h2>
          <button>Update Events</button>
        </>
      )}
    </>
  );
}

export { Studio };
