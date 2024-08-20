import React from 'react';
import { paths, operations, components } from '../../../openapi_schema';
import { ExtractResponseTypes } from '../../../types';
import { useBackendApiCall } from '../../../utils/Api';

const API_PATH = '/pages/profile/';
const API_METHOD = 'get';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_PATH][typeof API_METHOD]['responses']
>;

function Profile() {
  const {
    data: apiData,
    loading,
    response,
  } = useBackendApiCall<ResponseTypesByStatus[keyof ResponseTypesByStatus]>({
    endpoint: API_PATH,
    method: API_METHOD,
  });

  if (loading || response.status == 200) {
    const data = apiData as ResponseTypesByStatus['200'];

    if (loading) {
      return <p>loading</p>;
    }

    return (
      <>
        <h1>{data.email}</h1>
        <h1>{data.username}</h1>
      </>
    );
  } else if (response.status == 401) {
    <p>Login to continue</p>;

    // Redirect to login page
  }

  return <p>Profile</p>;
}

export { Profile };
