import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { paths, operations, components } from '../openapi_schema';
import { ExtractResponseTypes } from '../types';
import { useBackendApiCall } from '../utils/Api';
import { deleteStudioFunc } from '../components/Studio/deleteStudioFunc';

const API_PATH = '/pages/studios/{studio_id}/';
const API_METHOD = 'get';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_PATH][typeof API_METHOD]['responses']
>;

function Studio(): JSX.Element {
  const { studioId } = useParams();
  const {
    data: apiData,
    loading,
    response,
  } = useBackendApiCall<ResponseTypesByStatus[keyof ResponseTypesByStatus]>({
    endpoint: API_PATH.replace('{studio_id}', studioId),
    method: 'GET',
  });

  if (loading || response.status == 200) {
    // make data
    const data = apiData as ResponseTypesByStatus['200'];
    return (
      <div>
        <h1>{data === null ? 'loading...' : data.studio.name}</h1>
      </div>
    );
  } else if (response.status == 404) {
    const data = apiData as ResponseTypesByStatus['404'];
    return (
      <div>
        <h1>Studio not found</h1>
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

export { Studio };
