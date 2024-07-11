import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { callApi, useApiData } from '../utils/Api';
import { paths, operations, components } from '../openapi_schema';

const API_PATH = '/pages/studios/{studio_id}/';

function Studio(): JSX.Element {
  const { studioId } = useParams();

  const [data, setData, loading, setLoading, status, setStatus] = useApiData<
    | paths[typeof API_PATH]['get']['responses']['200']['content']['application/json']
  >(API_PATH.replace('{studio_id}', studioId));

  if (!loading && status !== 200) {
    return (
      <div>
        <h1>Studio not found</h1>
      </div>
    );
  }

  return (
    <div>
      <h1>{data !== null && data.studio.name}</h1>
    </div>
  );
}

export { Studio };
