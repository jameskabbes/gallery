import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { callApi, useApiData } from '../utils/Api';
import { paths, operations, components } from '../openapi_schema';
import { ApiResponse, ExtractResponseTypes } from '../types';

const API_PATH = '/pages/studios/{studio_id}/';
const API_METHOD = 'get';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_PATH][typeof API_METHOD]['responses']
>;

function Studio(): JSX.Element {
  const { studioId } = useParams();
  const { apiData, loading, status } = useApiData<
    ResponseTypesByStatus[keyof ResponseTypesByStatus]
  >(API_PATH.replace('{studio_id}', studioId));

  if (loading || status == 200) {
    // make data
    const data = apiData as ResponseTypesByStatus['200'];
    return (
      <div>
        <h1>{data === null ? 'loading...' : data.studio.name}</h1>
      </div>
    );
  } else if (status == 404) {
    const data = apiData as ResponseTypesByStatus['404'];
    return (
      <div>
        <h1>Studio not found</h1>
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

export { Studio };
