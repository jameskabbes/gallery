import React from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useLocation } from 'react-router-dom';
import { callApi, useApiCall } from '../../utils/Api';
import { paths, operations, components } from '../../openapi_schema';
import { ExtractResponseTypes } from '../../types';

const API_ENDPOINT = '/auth/verify-magic-link/';
const API_METHOD = 'post';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

function VerifyMagicLink() {
  const access_token: paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['query']['access_token'] =
    new URLSearchParams(useLocation().search).get('access_token');

  console.log(access_token);

  const {
    data: apiData,
    loading,
    response,
  } = useApiCall<
    ResponseTypesByStatus[keyof ResponseTypesByStatus],
    paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['query']
  >(
    {
      endpoint: API_ENDPOINT.replace('{access_token}', access_token),
      method: API_METHOD,
      data: { access_token: access_token },
    },
    true,
    [access_token]
  );

  if (!loading) {
    console.log(apiData);
  }

  return (
    <div>
      <p>Verifying your magic link...</p>
      {loading && <p>Loading...</p>}
    </div>
  );
}

export { VerifyMagicLink };
