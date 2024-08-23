import React, { useContext, useEffect, useRef } from 'react';
import { paths, operations, components } from '../../../openapi_schema';
import { ExtractResponseTypes } from '../../../types';
import { useBackendApiCall } from '../../../utils/Api';
import { AuthContext } from '../../../contexts/Auth';

const API_PATH = '/pages/profile/';
const API_METHOD = 'get';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_PATH][typeof API_METHOD]['responses']
>;

function Profile() {
  const authContext = useContext(AuthContext);
  const hasReloaded = useRef(false); // Add a ref to track the reload

  const {
    data: apiData,
    loading,
    response,
  } = useBackendApiCall<ResponseTypesByStatus[keyof ResponseTypesByStatus]>(
    {
      endpoint: API_PATH,
      method: API_METHOD,
    },
    true
  );

  if (loading || response.status == 200) {
    const data = apiData as ResponseTypesByStatus['200'];

    if (loading) {
      return <p>loading</p>;
    }

    return (
      <>
        <h1>{data.user.id}</h1>
        <h1>{data.user.username}</h1>
        <h1>{data.user.email}</h1>
      </>
    );
  } else {
    authContext.dispatch({ type: 'LOGOUT' });

    return <p>Login to continue</p>;
  }
}

export { Profile };
